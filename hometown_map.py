import pandas as pd
import requests
import folium
from folium import IFrame
from urllib.parse import quote

# =======================
MAPBOX_TOKEN = "<MAPBOX_TOKEN>"
MAPBOX_USERNAME = "hallirshea"
MAPBOX_STYLE_ID = "cmm9mgsot000s01s59gifcql3"
CSV_PATH = "hometown_locations.csv"  
OUTPUT_HTML = "lab06_map.html"
# =======================

TILES_URL = (
    f"https://api.mapbox.com/styles/v1/{MAPBOX_USERNAME}/{MAPBOX_STYLE_ID}/tiles/256/{{z}}/{{x}}/{{y}}"
    f"?access_token={MAPBOX_TOKEN}"
)
ATTRIBUTION = "© Mapbox © OpenStreetMap"

def geocode_address(address: str):
    """Return (lat, lon) from Mapbox geocoding or None if not found."""
    if not isinstance(address, str) or not address.strip():
        return None

    q = quote(address.strip())
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{q}.json"
    r = requests.get(url, params={"access_token": MAPBOX_TOKEN, "limit": 1}, timeout=20)
    r.raise_for_status()
    data = r.json()

    feats = data.get("features", [])
    if not feats:
        return None

    lon, lat = feats[0]["center"]  # Mapbox returns [lon, lat]
    return lat, lon

# ---- Load CSV ----
df = pd.read_csv(CSV_PATH)

# ---- Geocode each row ----
coords = []
failed = []

for _, row in df.iterrows():
    res = geocode_address(str(row["Address"]))
    if res is None:
        coords.append((None, None))
        failed.append((row.get("Name", "Unknown"), row.get("Address", "")))
    else:
        coords.append(res)

df["lat"] = [c[0] for c in coords]
df["lon"] = [c[1] for c in coords]

if failed:
    print("\nCould not geocode these (try shortening address like 'Place, Fort Worth, TX'):")
    for name, addr in failed:
        print(f"- {name}: {addr}")

df_ok = df.dropna(subset=["lat", "lon"]).copy()
if df_ok.empty:
    raise ValueError("No locations geocoded. Check your token and addresses.")

# ---- Build map ----
center = [df_ok["lat"].mean(), df_ok["lon"].mean()]
m = folium.Map(location=center, zoom_start=12, tiles=None)
folium.TileLayer(tiles=TILES_URL, attr=ATTRIBUTION, control=False).add_to(m)

# ---- Pretty marker styles (color + icon) ----
type_style = {
    "Sports":       {"color": "purple",    "icon": "flag"},
    "Park":         {"color": "green",     "icon": "tree-conifer"},
    "Bar":          {"color": "red",       "icon": "glass"},
    "Landmark":     {"color": "blue",      "icon": "star"},
    "Hotel":        {"color": "cadetblue", "icon": "home"},
    "Restaurant":   {"color": "orange",    "icon": "cutlery"},
    "Neighborhood": {"color": "gray",      "icon": "info-sign"},
    "Shopping":     {"color": "darkgreen", "icon": "shopping-cart"},
}

# ---- Add markers ----
for _, row in df_ok.iterrows():
    name = str(row["Name"])
    place_type = str(row["Type"])
    desc = str(row["Description"])
    img = str(row["Image_URL"]) if "Image_URL" in df_ok.columns and pd.notna(row["Image_URL"]) else ""

    style = type_style.get(place_type, {"color": "black", "icon": "info-sign"})

    img_html = ""
    if img.startswith("http"):
        img_html = f'<img src="{img}" style="width:260px;height:auto;border-radius:10px;margin-top:8px;">'

    html = f"""
    <div style="width:260px;">
      <h4 style="margin:0 0 6px 0;">{name}</h4>
      <div style="font-size:13px; line-height:1.3;">
        <b>Type:</b> {place_type}<br>
        {desc}
      </div>
      {img_html}
    </div>
    """

    popup = folium.Popup(IFrame(html=html, width=280, height=320), max_width=320)

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup,
        tooltip=name,
        icon=folium.Icon(color=style["color"], icon=style["icon"]),
    ).add_to(m)

# ---- Save ----
m.save(OUTPUT_HTML)
print(f"Map saved as {OUTPUT_HTML}")
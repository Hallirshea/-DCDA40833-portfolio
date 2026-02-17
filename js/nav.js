document.documentElement.classList.add('js');

document.addEventListener('DOMContentLoaded', function () {
    var mobileQuery = window.matchMedia('(max-width: 768px)');

    document.querySelectorAll('.site-nav').forEach(function (nav) {
        var toggleButton = nav.querySelector('.nav-toggle');
        var navLinks = nav.querySelector('.nav-links');

        if (!toggleButton || !navLinks) {
            return;
        }

        function closeMenu() {
            nav.classList.remove('is-open');
            toggleButton.setAttribute('aria-expanded', 'false');
        }

        toggleButton.addEventListener('click', function () {
            var isOpen = nav.classList.toggle('is-open');
            toggleButton.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                if (mobileQuery.matches) {
                    closeMenu();
                }
            });
        });

        window.addEventListener('resize', function () {
            if (!mobileQuery.matches) {
                closeMenu();
            }
        });
    });
});

(function () {

    const root = document.documentElement;

    const toggle = document.querySelector('[data-theme-toggle]');

    let theme =
        window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light';

    root.setAttribute('data-theme', theme);

    const renderIcon = () => {

    };

    renderIcon();

    toggle.addEventListener('click', function () {

        theme =
            theme === 'dark'
                ? 'light'
                : 'dark';

        root.setAttribute('data-theme', theme);

        renderIcon();
    });

})();

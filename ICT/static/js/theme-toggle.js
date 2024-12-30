document.getElementById('theme-toggle').addEventListener('click', function() {
    var stylesheet = document.getElementById('theme-stylesheet');
    if (stylesheet.getAttribute('href').includes('light.css')) {
        stylesheet.setAttribute('href', '/static/dark.css');
    } else {
        stylesheet.setAttribute('href', '/static/light.css');
    }
});

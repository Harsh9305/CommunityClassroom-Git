document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // --- 1. SET INITIAL THEME ON PAGE LOAD ---
    // Check for a saved theme in localStorage, or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', currentTheme);

    // --- 2. THEME TOGGLE EVENT LISTENER ---
    themeToggle.addEventListener('click', () => {
        // Get the current theme
        const theme = htmlElement.getAttribute('data-theme');

        // Switch to the opposite theme
        const newTheme = theme === 'light' ? 'dark' : 'light';

        // Apply the new theme to the <html> element
        htmlElement.setAttribute('data-theme', newTheme);

        // Save the new theme to localStorage
        localStorage.setItem('theme', newTheme);
    });
});

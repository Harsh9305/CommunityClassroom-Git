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

    // --- 3. COMPANY SEARCH FORM HANDLING ---
    const companySearchForm = document.getElementById('company-search-form');
    const companyNameInput = document.getElementById('company-name');
    const resultsContainer = document.getElementById('company-search-results');

    if (companySearchForm) {
        companySearchForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent default form submission

            const companyName = companyNameInput.value.trim();
            if (!companyName) {
                resultsContainer.innerHTML = '<p class="error">Please enter a company name.</p>';
                return;
            }

            // Show a loading state
            resultsContainer.innerHTML = '<p class="loading">Verifying, please wait...</p>';

            try {
                const response = await fetch('/verify-company', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ company_name: companyName }),
                });

                const data = await response.json();

                // Build the results HTML
                let resultsHtml = '';
                if (response.ok) {
                    resultsHtml = `
                        <p class="success">${data.message}</p>
                        <h4>Details Found:</h4>
                        <ul>
                            ${data.details.map(detail => `<li>${detail}</li>`).join('')}
                        </ul>
                    `;
                } else {
                    resultsHtml = `<p class="error">${data.message || 'An unknown error occurred.'}</p>`;
                }
                resultsContainer.innerHTML = resultsHtml;

            } catch (error) {
                resultsContainer.innerHTML = `<p class="error">An error occurred while connecting to the server: ${error.message}</p>`;
            }
        });
    }
});

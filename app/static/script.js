document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    // Set initial theme from localStorage or default to dark
    const currentTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', currentTheme);
    themeToggle.textContent = currentTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';

    themeToggle.addEventListener('click', () => {
        const newTheme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        themeToggle.textContent = newTheme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
    });

    // Chart.js implementation
    const chartCanvas = document.getElementById('skillMatchChart');
    if (chartCanvas) {
        const matchPercentage = parseFloat(chartCanvas.dataset.match);
        const remainingPercentage = 100 - matchPercentage;

        new Chart(chartCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Skill Match', 'Missing Skills'],
                datasets: [{
                    data: [matchPercentage, remainingPercentage],
                    backgroundColor: [
                        getComputedStyle(html).getPropertyValue('--primary-color').trim(),
                        getComputedStyle(html).getPropertyValue('--card-bg-color').trim()
                    ],
                    borderColor: getComputedStyle(html).getPropertyValue('--bg-color').trim(),
                    borderWidth: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: true
                    }
                }
            }
        });
    }
});

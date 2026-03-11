// Global theme management script
// This file should be included in all pages to maintain consistent theme

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        updateThemeButton(true);
    }
}

function toggleTheme() {
    const body = document.body;
    const isLight = body.classList.toggle('light-theme');
    
    // Save preference globally
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
    
    // Update button text if present
    updateThemeButton(isLight);
}

function updateThemeButton(isLight) {
    const text = document.getElementById('themeText');
    if (text) {
        text.textContent = isLight ? 'Темная тема' : 'Светлая тема';
    }
}

// Auto-initialize theme on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
} else {
    initTheme();
}

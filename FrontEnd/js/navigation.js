// Add active class to current page navigation
document.addEventListener('DOMContentLoaded', () => {
    const currentPage = location.pathname.split('/').pop();
    document.querySelectorAll('.nav-button').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        }
    });
});
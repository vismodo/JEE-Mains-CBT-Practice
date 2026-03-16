// Minimal JS for site
document.addEventListener('DOMContentLoaded', function () {
  // Example: add a small fade-in for main content
  const main = document.querySelector('main');
  if (main) {
    main.style.opacity = 0;
    main.style.transition = 'opacity 300ms ease-in-out';
    requestAnimationFrame(() => { main.style.opacity = 1; });
  }
});
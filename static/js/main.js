// Navigation Interactions
const navLinks = document.querySelectorAll('nav ul li a');
navLinks.forEach(link => {
    link.addEventListener('click', function() {
        navLinks.forEach(link => link.classList.remove('active'));
        this.classList.add('active');
    });
});

// Smooth Scrolling
const smoothScroll = (target, duration) => {
    const targetPosition = document.querySelector(target).offsetTop;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    const animation = currentTime => {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    };

    const ease = (t, b, c, d) => {
        t /= d / 2;
        if (t < 1) return c / 2 * t * t + b;
        t--;
        return -c / 2 * (t * (t - 2) - 1) + b;
    };

    requestAnimationFrame(animation);
};

// Example usage: smoothScroll('.target-element', 1000);

// Dynamic Content Loading for API Endpoints
async function loadWallets() {
    try {
        const response = await fetch('/api/wallets');
        const data = await response.json();
        console.log(data);
        // Handle data to update the UI
    } catch (error) {
        console.error('Error loading wallets:', error);
    }
}

// Call the function to load wallets
loadWallets();
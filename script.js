// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form submission handler
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const email = this.querySelector('input[type="email"]').value;
        const message = this.querySelector('textarea').value;
        
        // Show success message
        alert('Thank you for your message! We\'ll get back to you soon.');
        
        // Reset form
        this.reset();
    });
}

// Add scroll animation to feature cards
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.querySelectorAll('.feature-card, .step').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Navbar background on scroll
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.15)';
    } else {
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }
});

// Initialize
console.log('Ragab AI Trade Website Loaded');

const API_BASE = "http://127.0.0.1:8001";

async function loadTradingDashboard() {
    const token = localStorage.getItem("ragab_token");
    const accountId = localStorage.getItem("ragab_ai_trade_account_id");

    if (!token || !accountId) return;

    try {
        const response = await fetch(
            `${API_BASE}/api/v1/trading-accounts/${accountId}/summary`,
            { headers: { Authorization: `Bearer ${token}` } }
        );

        if (!response.ok) throw new Error("Dashboard request failed");

        const account = await response.json();

        const positionsResponse = await fetch(
            `${API_BASE}/api/v1/paper/positions`,
            { headers: { Authorization: `Bearer ${token}` } }
        );

        if (!positionsResponse.ok) throw new Error("Positions request failed");

        const positions = await positionsResponse.json();
        const openPositions = positions.filter(position => position.status === "open");

        const signalResponse = await fetch(
            `${API_BASE}/api/v1/automation/market-signal`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    trading_account_id: accountId,
                    symbol: "XAUUSD",
                    timeframe: "M5",
                    period: 3,
                    quantity: "1"
                })
            }
        );

        if (!signalResponse.ok) throw new Error("Market signal request failed");

        const signal = await signalResponse.json();

        const equity = document.querySelector("#dashboard-equity");
        const pnl = document.querySelector("#dashboard-pnl");
        const openPositionsElement = document.querySelector("#dashboard-open-positions");
        const buySignal = document.querySelector("#dashboard-buy-signal");
        const sellSignals = document.querySelector("#dashboard-sell-signals");

        if (equity) equity.textContent = `$${Number(account.equity).toFixed(2)}`;
        if (pnl) pnl.textContent = `$${Number(account.unrealized_pnl).toFixed(2)} Unrealized`;
        if (openPositionsElement) openPositionsElement.textContent = openPositions.length;

        if (buySignal) buySignal.textContent = signal.signal === "BUY" ? "BUY" : "--";
        if (sellSignals) sellSignals.textContent = signal.signal === "SELL" ? "1" : "0";
    } catch (error) {
        console.error("Dashboard error:", error);
    }
}

loadTradingDashboard();

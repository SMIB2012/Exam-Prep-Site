// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard components
    initQuickStats();
    initProgressCharts();
    initRecentActivity();
    initQuickActions();
    
    // Auto-refresh stats every 30 seconds
    setInterval(updateStats, 30000);
});

// Initialize quick stats cards
function initQuickStats() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach((card, index) => {
        // Add entrance animation
        card.style.animationDelay = `${index * 100}ms`;
        card.classList.add('fade-in-up');
        
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.05)';
        });
    });
    
    // Animate stat numbers
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(number => {
        animateNumber(number);
    });
}

// Initialize progress charts
function initProgressCharts() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('data-width') || bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1.5s ease-in-out';
            bar.style.width = targetWidth;
        }, 500);
    });
}

// Initialize recent activity section
function initRecentActivity() {
    const activityItems = document.querySelectorAll('.activity-item');
    
    activityItems.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.4s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
        }, index * 150);
    });
}

// Initialize quick action buttons
function initQuickActions() {
    const actionButtons = document.querySelectorAll('.quick-action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            // Remove ripple after animation
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Animate numbers counting up
function animateNumber(element) {
    const target = parseInt(element.getAttribute('data-target') || element.textContent);
    const duration = 2000;
    const start = 0;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.floor(start + (target - start) * easeOut);
        
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        } else {
            element.textContent = target.toLocaleString();
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// Update stats (for real-time updates)
function updateStats() {
    // This would typically fetch new data from the server
    // For now, we'll just add a subtle animation to indicate refresh
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        card.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => {
            card.style.animation = '';
        }, 500);
    });
}

// Study session timer
function initStudyTimer() {
    const timerElement = document.getElementById('study-timer');
    if (!timerElement) return;
    
    let seconds = 0;
    const interval = setInterval(() => {
        seconds++;
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        timerElement.textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }, 1000);
    
    // Store timer in session to persist across page reloads
    sessionStorage.setItem('studyTimer', interval);
}

// Welcome message based on time of day
function initWelcomeMessage() {
    const welcomeElement = document.querySelector('.welcome-message');
    if (!welcomeElement) return;
    
    const hour = new Date().getHours();
    let greeting;
    
    if (hour < 12) {
        greeting = 'Good morning';
    } else if (hour < 18) {
        greeting = 'Good afternoon';
    } else {
        greeting = 'Good evening';
    }
    
    const userName = welcomeElement.getAttribute('data-user-name') || 'Student';
    welcomeElement.textContent = `${greeting}, ${userName}!`;
}

// Initialize tooltips for dashboard elements
function initDashboardTooltips() {
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element);
    });
}

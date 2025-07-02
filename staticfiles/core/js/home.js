// Enhanced Home Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all animations and interactions
    initScrollAnimations();
    initCounterAnimations();
    initParallaxEffects();
    initSmoothScrolling();
    initHeroAnimations();
    initTooltips();
    initHeroButtons(); // Add hero button initialization
    
    // Initialize performance optimizations
    initIntersectionObserver();
    initLazyLoading();
});

// Initialize Hero Buttons with enhanced interactions
function initHeroButtons() {
    const heroButtons = document.querySelectorAll('.hero-btn');
    
    heroButtons.forEach(button => {
        // Add click animation
        button.addEventListener('mousedown', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Add focus handling for accessibility
        button.addEventListener('focus', function() {
            this.style.outline = '3px solid rgba(255, 193, 7, 0.5)';
            this.style.outlineOffset = '2px';
        });
        
        button.addEventListener('blur', function() {
            this.style.outline = 'none';
        });
        
        // Add loading state for better UX
        button.addEventListener('click', function(e) {
            const originalText = this.innerHTML;
            const isLogin = this.href.includes('login');
            const isRegister = this.href.includes('register');
            
            if (isLogin || isRegister) {
                this.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 8px;"></i>Loading...';
                this.style.pointerEvents = 'none';
                
                // Restore original state if navigation fails
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.style.pointerEvents = 'auto';
                }, 3000);
            }
        });
    });
}

// Enhanced scroll animations with staggered delays
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in-up, .fade-in, .slide-in-left, .slide-in-right, .scale-in');
    
    if ('IntersectionObserver' in window) {
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const delay = entry.target.dataset.delay || 0;
                    
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, parseInt(delay));
                    
                    // Unobserve after animation to improve performance
                    animationObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        animatedElements.forEach(el => {
            animationObserver.observe(el);
        });
    } else {
        // Fallback for browsers without IntersectionObserver
        animatedElements.forEach(el => {
            const delay = el.dataset.delay || 0;
            setTimeout(() => {
                el.classList.add('visible');
            }, parseInt(delay));
        });
    }
}

// Enhanced counter animations with easing
function initCounterAnimations() {
    const counters = document.querySelectorAll('.stat-number');
    
    const animateCounter = (element, target, suffix = '') => {
        let current = 0;
        const increment = target / 100;
        const duration = 2000; // 2 seconds
        const stepTime = duration / 100;
        
        const timer = setInterval(() => {
            current += increment;
            
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            // Apply easing function
            const progress = current / target;
            const easedProgress = easeOutCubic(progress);
            const displayValue = Math.floor(target * easedProgress);
            
            element.textContent = displayValue + suffix;
        }, stepTime);
    };
    
    // Easing function for smooth animation
    function easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }
    
    if ('IntersectionObserver' in window) {
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const target = parseInt(element.dataset.target);
                    
                    if (target > 0) {
                        const originalText = element.textContent;
                        const hasPlus = originalText.includes('+');
                        const hasPercent = originalText.includes('%');
                        
                        let suffix = '';
                        if (hasPercent) suffix = '%';
                        else if (hasPlus) suffix = '+';
                        
                        animateCounter(element, target, suffix);
                        counterObserver.unobserve(element);
                    }
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => {
            counterObserver.observe(counter);
        });
    }
}

// Enhanced parallax effects
function initParallaxEffects() {
    const heroSection = document.querySelector('.hero-section');
    const floatingElements = document.querySelectorAll('.float-element');
    
    if (heroSection && window.innerWidth > 768) {
        let ticking = false;
        
        function updateParallax() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.3;
            
            heroSection.style.transform = `translateY(${rate}px)`;
            
            // Animate floating elements
            floatingElements.forEach((element, index) => {
                const speed = 0.2 + (index * 0.1);
                const yPos = scrolled * speed;
                element.style.transform = `translateY(${yPos}px) rotate(${scrolled * 0.02}deg)`;
            });
            
            ticking = false;
        }
        
        function requestParallax() {
            if (!ticking) {
                requestAnimationFrame(updateParallax);
                ticking = true;
            }
        }
        
        window.addEventListener('scroll', requestParallax, { passive: true });
    }
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const scrollLinks = document.querySelectorAll('a[href^="#"]');
    
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                
                const offsetTop = target.offsetTop - 80; // Account for navbar height
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add smooth scrolling for scroll indicator
    const scrollIndicator = document.querySelector('.hero-scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', function() {
            const statsSection = document.querySelector('#stats');
            if (statsSection) {
                const offsetTop = statsSection.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    }
}

// Hero section entrance animations
function initHeroAnimations() {
    const heroElements = document.querySelectorAll('.hero-title, .hero-subtitle, .hero-cta-buttons, .hero-image');
    
    heroElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 200}ms`;
        element.classList.add('fade-in-up');
        
        // Trigger animation immediately for hero section
        setTimeout(() => {
            element.classList.add('visible');
        }, index * 200);
    });
}

// Enhanced tooltips for stats with smart positioning
function initTooltips() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        const tooltip = card.querySelector('.stat-tooltip');
        
        if (tooltip) {
            card.addEventListener('mouseenter', function() {
                // Check if tooltip would go outside viewport
                const rect = card.getBoundingClientRect();
                const tooltipRect = tooltip.getBoundingClientRect();
                const viewportWidth = window.innerWidth;
                
                // Reset positioning classes
                tooltip.classList.remove('tooltip-left', 'tooltip-right', 'tooltip-center');
                
                // Smart positioning based on card position
                if (rect.left < 150) {
                    tooltip.classList.add('tooltip-left');
                } else if (rect.right > viewportWidth - 150) {
                    tooltip.classList.add('tooltip-right');
                } else {
                    tooltip.classList.add('tooltip-center');
                }
                
                // Show tooltip
                tooltip.style.opacity = '1';
                tooltip.style.visibility = 'visible';
                tooltip.style.transform = tooltip.classList.contains('tooltip-center') 
                    ? 'translateX(-50%) translateY(-10px)' 
                    : 'translateY(-10px)';
            });
            
            card.addEventListener('mouseleave', function() {
                tooltip.style.opacity = '0';
                tooltip.style.visibility = 'hidden';
                tooltip.style.transform = tooltip.classList.contains('tooltip-center') 
                    ? 'translateX(-50%) translateY(0)' 
                    : 'translateY(0)';
            });
        }
    });
}

// Performance optimizations
function initIntersectionObserver() {
    // Optimize animations for elements not in viewport
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-viewport');
            } else {
                entry.target.classList.remove('in-viewport');
            }
        });
    }, {
        threshold: 0.1
    });
    
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        observer.observe(section);
    });
}

// Lazy loading for images and heavy content
function initLazyLoading() {
    const lazyElements = document.querySelectorAll('[data-lazy]');
    
    if ('IntersectionObserver' in window) {
        const lazyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const src = element.dataset.lazy;
                    
                    if (src) {
                        element.src = src;
                        element.classList.add('loaded');
                    }
                    
                    lazyObserver.unobserve(element);
                }
            });
        });
        
        lazyElements.forEach(element => {
            lazyObserver.observe(element);
        });
    }
}

// Enhanced feature card interactions
const featureCards = document.querySelectorAll('.feature-card');
featureCards.forEach((card, index) => {
    // Add entrance animation delay
    card.style.animationDelay = `${index * 100}ms`;
    
    // Enhanced hover effects
    card.addEventListener('mouseenter', function() {
        const icon = this.querySelector('.pulse-icon');
        if (icon) {
            icon.style.animation = 'pulse-strong 0.6s ease-in-out';
        }
    });
    
    card.addEventListener('mouseleave', function() {
        const icon = this.querySelector('.pulse-icon');
        if (icon) {
            icon.style.animation = 'pulse-subtle 2s ease-in-out infinite';
        }
    });
});

// Enhanced subject card interactions
const subjectCards = document.querySelectorAll('.subject-card');
subjectCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px) scale(1.02)';
        
        const icon = this.querySelector('.subject-icon i');
        if (icon) {
            icon.style.transform = 'scale(1.1) rotate(5deg)';
            icon.style.color = '#0d6efd';
        }
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0) scale(1)';
        
        const icon = this.querySelector('.subject-icon i');
        if (icon) {
            icon.style.transform = 'scale(1) rotate(0deg)';
            icon.style.color = '';
        }
    });
});

// CTA section special effects
const ctaSection = document.querySelector('.cta-section');
if (ctaSection) {
    const ctaObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Add special pulse animation to CTA buttons
                const ctaButtons = entry.target.querySelectorAll('.cta-pulse');
                ctaButtons.forEach((button, index) => {
                    setTimeout(() => {
                        button.style.animation = 'pulse-cta 2s ease-in-out infinite';
                    }, index * 300);
                });
            }
        });
    }, { threshold: 0.3 });
    
    ctaObserver.observe(ctaSection);
}

// Error handling and fallbacks
window.addEventListener('error', function(e) {
    console.warn('Animation error caught:', e.error);
    // Fallback: remove problematic animations
    document.querySelectorAll('[style*="animation"]').forEach(el => {
        el.style.animation = 'none';
    });
});

// Accessibility: Respect reduced motion preferences
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.documentElement.style.setProperty('--animation-duration', '0.01ms');
    document.querySelectorAll('[class*="fade"], [class*="slide"], [class*="scale"]').forEach(el => {
        el.classList.add('visible');
    });
}

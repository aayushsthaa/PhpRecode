// Echhapa News Portal Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeLazyLoading();
    initializeNewsletterForm();
    initializeSocialSharing();
    initializeSearchFunctionality();
    initializeReadingProgress();
    initializeMobileMenu();
});

// Lazy loading for images
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    img.classList.add('fade-in');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Newsletter subscription
function initializeNewsletterForm() {
    const newsletterForms = document.querySelectorAll('.newsletter-widget form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            const button = this.querySelector('button[type="submit"]');
            const originalText = button.innerHTML;
            
            // Validate email
            if (!isValidEmail(email)) {
                showNotification('Please enter a valid email address.', 'warning');
                return;
            }
            
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subscribing...';
            button.disabled = true;
            
            // Simulate API call (replace with actual endpoint)
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-check"></i> Subscribed!';
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
                
                showNotification('Thank you for subscribing to our newsletter!', 'success');
                
                // Reset form after delay
                setTimeout(() => {
                    this.reset();
                    button.innerHTML = originalText;
                    button.disabled = false;
                    button.classList.remove('btn-success');
                    button.classList.add('btn-primary');
                }, 3000);
            }, 2000);
        });
    });
}

// Social media sharing
function initializeSocialSharing() {
    // Add share buttons to articles
    const articleContent = document.querySelector('.article-content');
    if (articleContent) {
        const shareContainer = document.createElement('div');
        shareContainer.className = 'share-buttons text-center py-4';
        shareContainer.innerHTML = `
            <h6 class="mb-3">Share this article</h6>
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-outline-primary" onclick="shareOnFacebook()">
                    <i class="fab fa-facebook-f"></i> Facebook
                </button>
                <button type="button" class="btn btn-outline-info" onclick="shareOnTwitter()">
                    <i class="fab fa-twitter"></i> Twitter
                </button>
                <button type="button" class="btn btn-outline-success" onclick="shareOnWhatsApp()">
                    <i class="fab fa-whatsapp"></i> WhatsApp
                </button>
                <button type="button" class="btn btn-outline-secondary" onclick="copyToClipboard()">
                    <i class="fas fa-link"></i> Copy Link
                </button>
            </div>
        `;
        
        articleContent.appendChild(shareContainer);
    }
}

// Share functions
function shareOnFacebook() {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=600,height=400');
}

function shareOnTwitter() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', 'width=600,height=400');
}

function shareOnWhatsApp() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://wa.me/?text=${text} ${url}`, '_blank');
}

function copyToClipboard() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        showNotification('Link copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy link.', 'error');
    });
}

// Search functionality
function initializeSearchFunctionality() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[type="search"]');
        const searchResults = document.querySelector('.search-results');
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length < 3) {
                if (searchResults) searchResults.innerHTML = '';
                return;
            }
            
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, 500);
        });
    }
}

function performSearch(query) {
    // Implement search functionality
    console.log('Searching for:', query);
    // This would typically make an AJAX request to a search endpoint
}

// Reading progress indicator
function initializeReadingProgress() {
    const article = document.querySelector('.article-content');
    if (article) {
        const progressBar = document.createElement('div');
        progressBar.className = 'reading-progress';
        progressBar.innerHTML = '<div class="progress-fill"></div>';
        
        const style = document.createElement('style');
        style.textContent = `
            .reading-progress {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: rgba(0,0,0,0.1);
                z-index: 1000;
            }
            .progress-fill {
                height: 100%;
                background: #dc3545;
                width: 0%;
                transition: width 0.3s ease;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(progressBar);
        
        const progressFill = progressBar.querySelector('.progress-fill');
        
        window.addEventListener('scroll', () => {
            const articleTop = article.offsetTop;
            const articleHeight = article.offsetHeight;
            const windowHeight = window.innerHeight;
            const scrollTop = window.pageYOffset;
            
            const progress = Math.min(
                100,
                Math.max(0, (scrollTop - articleTop + windowHeight) / articleHeight * 100)
            );
            
            progressFill.style.width = progress + '%';
        });
    }
}

// Mobile menu handling
function initializeMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking on links
        navbarCollapse.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                }
            });
        });
    }
}

// Utility functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
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

// Back to top button
function initializeBackToTop() {
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTopButton.className = 'btn btn-primary btn-sm position-fixed';
    backToTopButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px; display: none;';
    backToTopButton.title = 'Back to top';
    
    document.body.appendChild(backToTopButton);
    
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    backToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Initialize back to top button
initializeBackToTop();

// Performance optimization: Defer non-critical scripts
window.addEventListener('load', function() {
    // Initialize non-critical features after page load
    initializeAnalytics();
    initializeComments();
});

function initializeAnalytics() {
    // Initialize analytics tracking
    console.log('Analytics initialized');
}

function initializeComments() {
    // Initialize comment system if present
    const commentSection = document.querySelector('.comments-section');
    if (commentSection) {
        console.log('Comments system initialized');
    }
}

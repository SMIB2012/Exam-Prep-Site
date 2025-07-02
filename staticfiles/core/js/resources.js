// Resources JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize resources functionality
    initResourceFilters();
    initResourceCards();
    initSearchFunctionality();
    initResourceActions();
    initBookmarkSystem();
    initProgressTracking();
    initDownloadTracking();
});

// Initialize resource filters
function initResourceFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const subjectFilter = document.getElementById('subject-filter');
    const typeFilter = document.getElementById('type-filter');
    const difficultyFilter = document.getElementById('difficulty-filter');
    
    // Filter button handlers
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Apply filter
            const filterValue = this.getAttribute('data-filter');
            applyResourceFilter('category', filterValue);
        });
    });
    
    // Subject filter handler
    if (subjectFilter) {
        subjectFilter.addEventListener('change', function() {
            applyResourceFilter('subject', this.value);
        });
    }
    
    // Type filter handler
    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            applyResourceFilter('type', this.value);
        });
    }
    
    // Difficulty filter handler
    if (difficultyFilter) {
        difficultyFilter.addEventListener('change', function() {
            applyResourceFilter('difficulty', this.value);
        });
    }
}

// Initialize resource cards
function initResourceCards() {
    const resourceCards = document.querySelectorAll('.resource-card');
    
    resourceCards.forEach((card, index) => {
        // Add entrance animation
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
        
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.05)';
        });
        
        // Add click tracking
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.resource-actions')) {
                trackResourceView(this.getAttribute('data-resource-id'));
            }
        });
    });
}

// Initialize search functionality
function initSearchFunctionality() {
    const searchInput = document.getElementById('resource-search');
    if (!searchInput) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.toLowerCase().trim();
        
        // Debounce search
        searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                performResourceSearch(query);
            } else {
                showAllResources();
            }
        }, 300);
    });
    
    // Clear search button
    const clearSearch = document.getElementById('clear-search');
    if (clearSearch) {
        clearSearch.addEventListener('click', function() {
            searchInput.value = '';
            showAllResources();
        });
    }
}

// Initialize resource actions
function initResourceActions() {
    // Download buttons
    const downloadBtns = document.querySelectorAll('.download-btn');
    downloadBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const resourceId = this.getAttribute('data-resource-id');
            const resourceType = this.getAttribute('data-resource-type');
            
            downloadResource(resourceId, resourceType);
        });
    });
    
    // View buttons
    const viewBtns = document.querySelectorAll('.view-btn');
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const resourceId = this.getAttribute('data-resource-id');
            const resourceUrl = this.getAttribute('href');
            
            viewResource(resourceId, resourceUrl);
        });
    });
    
    // Share buttons
    const shareBtns = document.querySelectorAll('.share-btn');
    shareBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const resourceUrl = this.getAttribute('data-share-url');
            const resourceTitle = this.getAttribute('data-share-title');
            
            shareResource(resourceUrl, resourceTitle);
        });
    });
}

// Initialize bookmark system
function initBookmarkSystem() {
    const bookmarkBtns = document.querySelectorAll('.bookmark-btn');
    
    bookmarkBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const resourceId = this.getAttribute('data-resource-id');
            const isBookmarked = this.classList.contains('bookmarked');
            
            toggleBookmark(resourceId, !isBookmarked, this);
        });
    });
}

// Initialize progress tracking
function initProgressTracking() {
    const progressBars = document.querySelectorAll('.progress-bar[data-progress]');
    
    progressBars.forEach(bar => {
        const progress = parseInt(bar.getAttribute('data-progress'));
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = `${progress}%`;
        }, 500);
    });
}

// Initialize download tracking
function initDownloadTracking() {
    // Track file downloads
    const downloadLinks = document.querySelectorAll('a[download]');
    
    downloadLinks.forEach(link => {
        link.addEventListener('click', function() {
            const fileName = this.getAttribute('download');
            const resourceId = this.getAttribute('data-resource-id');
            
            trackDownload(resourceId, fileName);
        });
    });
}

// Apply resource filter
function applyResourceFilter(filterType, filterValue) {
    const resourceCards = document.querySelectorAll('.resource-card');
    let visibleCount = 0;
    
    resourceCards.forEach(card => {
        let shouldShow = true;
        
        if (filterValue && filterValue !== 'all') {
            const cardValue = card.getAttribute(`data-${filterType}`);
            shouldShow = cardValue === filterValue;
        }
        
        if (shouldShow) {
            card.style.display = 'block';
            card.classList.add('fade-in');
            visibleCount++;
        } else {
            card.style.display = 'none';
            card.classList.remove('fade-in');
        }
    });
    
    // Update results count
    updateResultsCount(visibleCount);
}

// Perform resource search
function performResourceSearch(query) {
    const resourceCards = document.querySelectorAll('.resource-card');
    let visibleCount = 0;
    
    resourceCards.forEach(card => {
        const title = card.querySelector('.resource-title').textContent.toLowerCase();
        const description = card.querySelector('.resource-description')?.textContent.toLowerCase() || '';
        const tags = card.getAttribute('data-tags')?.toLowerCase() || '';
        
        const matchesSearch = title.includes(query) || 
                            description.includes(query) || 
                            tags.includes(query);
        
        if (matchesSearch) {
            card.style.display = 'block';
            highlightSearchTerms(card, query);
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    updateResultsCount(visibleCount);
}

// Show all resources
function showAllResources() {
    const resourceCards = document.querySelectorAll('.resource-card');
    
    resourceCards.forEach(card => {
        card.style.display = 'block';
        removeHighlights(card);
    });
    
    updateResultsCount(resourceCards.length);
}

// Highlight search terms
function highlightSearchTerms(card, query) {
    const title = card.querySelector('.resource-title');
    const description = card.querySelector('.resource-description');
    
    if (title) {
        const originalText = title.getAttribute('data-original-text') || title.textContent;
        title.setAttribute('data-original-text', originalText);
        title.innerHTML = originalText.replace(new RegExp(query, 'gi'), '<mark>$&</mark>');
    }
    
    if (description) {
        const originalText = description.getAttribute('data-original-text') || description.textContent;
        description.setAttribute('data-original-text', originalText);
        description.innerHTML = originalText.replace(new RegExp(query, 'gi'), '<mark>$&</mark>');
    }
}

// Remove highlights
function removeHighlights(card) {
    const highlightedElements = card.querySelectorAll('[data-original-text]');
    
    highlightedElements.forEach(element => {
        const originalText = element.getAttribute('data-original-text');
        element.textContent = originalText;
        element.removeAttribute('data-original-text');
    });
}

// Update results count
function updateResultsCount(count) {
    const countElement = document.getElementById('results-count');
    if (countElement) {
        countElement.textContent = `${count} resource${count !== 1 ? 's' : ''} found`;
    }
}

// Download resource
function downloadResource(resourceId, resourceType) {
    showDownloadModal(resourceId, resourceType);
}

// View resource
function viewResource(resourceId, resourceUrl) {
    // Track view
    trackResourceView(resourceId);
    
    // Open resource
    if (resourceUrl.endsWith('.pdf')) {
        openPDFViewer(resourceUrl);
    } else {
        window.open(resourceUrl, '_blank');
    }
}

// Share resource
function shareResource(resourceUrl, resourceTitle) {
    if (navigator.share) {
        navigator.share({
            title: resourceTitle,
            url: resourceUrl
        }).catch(console.error);
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(resourceUrl).then(() => {
            showToast('Resource link copied to clipboard!', 'success');
        }).catch(() => {
            showShareModal(resourceUrl, resourceTitle);
        });
    }
}

// Toggle bookmark
function toggleBookmark(resourceId, isBookmarked, button) {
    const action = isBookmarked ? 'add' : 'remove';
    
    fetch(`/resources/bookmark/${resourceId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (isBookmarked) {
                button.classList.add('bookmarked');
                button.innerHTML = '<i class="fas fa-bookmark"></i>';
                button.title = 'Remove from bookmarks';
            } else {
                button.classList.remove('bookmarked');
                button.innerHTML = '<i class="far fa-bookmark"></i>';
                button.title = 'Add to bookmarks';
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Failed to update bookmark', 'error');
        }
    })
    .catch(error => {
        console.error('Error toggling bookmark:', error);
        showToast('Failed to update bookmark', 'error');
    });
}

// Track resource view
function trackResourceView(resourceId) {
    fetch(`/resources/track-view/${resourceId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    }).catch(error => {
        console.error('Error tracking view:', error);
    });
}

// Track download
function trackDownload(resourceId, fileName) {
    fetch(`/resources/track-download/${resourceId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ file_name: fileName })
    }).catch(error => {
        console.error('Error tracking download:', error);
    });
}

// Show download modal
function showDownloadModal(resourceId, resourceType) {
    const modal = document.getElementById('downloadModal');
    if (!modal) return;
    
    // Update modal content based on resource type
    const modalBody = modal.querySelector('.modal-body');
    const downloadLink = modal.querySelector('.download-link');
    
    modalBody.innerHTML = `
        <div class="text-center">
            <i class="fas fa-download fs-1 text-primary mb-3"></i>
            <h5>Download ${resourceType.charAt(0).toUpperCase() + resourceType.slice(1)}</h5>
            <p class="text-muted">This resource will be downloaded to your device.</p>
        </div>
    `;
    
    downloadLink.href = `/resources/download/${resourceId}/`;
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

// Show share modal
function showShareModal(resourceUrl, resourceTitle) {
    const modal = document.getElementById('shareModal');
    if (!modal) return;
    
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="text-center">
            <h5>Share Resource</h5>
            <p>${resourceTitle}</p>
            <div class="input-group mb-3">
                <input type="text" class="form-control" value="${resourceUrl}" readonly>
                <button class="btn btn-outline-secondary" type="button" onclick="copyToClipboard('${resourceUrl}')">
                    <i class="fas fa-copy"></i>
                </button>
            </div>
            <div class="d-flex justify-content-center gap-2">
                <a href="https://twitter.com/intent/tweet?url=${encodeURIComponent(resourceUrl)}&text=${encodeURIComponent(resourceTitle)}" 
                   target="_blank" class="btn btn-primary btn-sm">
                    <i class="fab fa-twitter"></i> Twitter
                </a>
                <a href="https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(resourceUrl)}" 
                   target="_blank" class="btn btn-primary btn-sm">
                    <i class="fab fa-facebook"></i> Facebook
                </a>
                <a href="https://wa.me/?text=${encodeURIComponent(resourceTitle + ' ' + resourceUrl)}" 
                   target="_blank" class="btn btn-success btn-sm">
                    <i class="fab fa-whatsapp"></i> WhatsApp
                </a>
            </div>
        </div>
    `;
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

// Open PDF viewer
function openPDFViewer(pdfUrl) {
    const viewerUrl = `/pdf-viewer/?file=${encodeURIComponent(pdfUrl)}`;
    window.open(viewerUrl, '_blank');
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Create toast container
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Copy to clipboard utility
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Get CSRF token
function getCsrfToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

// Lazy loading for resource images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy');
        });
    }
}

// Resource recommendations
function loadRecommendedResources() {
    const recommendationsContainer = document.getElementById('recommended-resources');
    if (!recommendationsContainer) return;
    
    fetch('/resources/recommendations/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.recommendations && data.recommendations.length > 0) {
            displayRecommendations(data.recommendations);
        }
    })
    .catch(error => {
        console.error('Error loading recommendations:', error);
    });
}

// Display recommendations
function displayRecommendations(recommendations) {
    const container = document.getElementById('recommended-resources');
    
    const html = recommendations.map(resource => `
        <div class="col-md-4 mb-3">
            <div class="card resource-card" data-resource-id="${resource.id}">
                <div class="card-body">
                    <h6 class="card-title">${resource.title}</h6>
                    <p class="card-text small text-muted">${resource.description}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">${resource.type}</small>
                        <button class="btn btn-sm btn-outline-primary view-btn" 
                                data-resource-id="${resource.id}" 
                                onclick="viewResource(${resource.id}, '${resource.url}')">
                            View
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

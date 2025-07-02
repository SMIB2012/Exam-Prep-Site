// Leaderboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize leaderboard components
    initLeaderboardTable();
    initFilterControls();
    initUserHighlight();
    initAnimations();
    initRefreshButton();
    
    // Auto-refresh leaderboard every 2 minutes
    setInterval(refreshLeaderboard, 120000);
});

// Initialize leaderboard table
function initLeaderboardTable() {
    const leaderboardTable = document.querySelector('.leaderboard-table');
    if (!leaderboardTable) return;
    
    // Add smooth entrance animation
    const rows = leaderboardTable.querySelectorAll('tbody tr');
    rows.forEach((row, index) => {
        row.style.opacity = '0';
        row.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            row.style.transition = 'all 0.4s ease';
            row.style.opacity = '1';
            row.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Add hover effects
    rows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
            this.style.transform = 'scale(1.02)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.transform = 'scale(1)';
        });
    });
    
    // Highlight top performers
    highlightTopPerformers();
}

// Initialize filter controls
function initFilterControls() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const subjectFilter = document.getElementById('subject-filter');
    const timeRangeFilter = document.getElementById('time-range-filter');
    
    // Filter button handlers
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Apply filter
            const filterType = this.getAttribute('data-filter');
            applyLeaderboardFilter(filterType);
        });
    });
    
    // Subject filter handler
    if (subjectFilter) {
        subjectFilter.addEventListener('change', function() {
            const selectedSubject = this.value;
            filterBySubject(selectedSubject);
        });
    }
    
    // Time range filter handler
    if (timeRangeFilter) {
        timeRangeFilter.addEventListener('change', function() {
            const selectedRange = this.value;
            filterByTimeRange(selectedRange);
        });
    }
}

// Initialize user highlight
function initUserHighlight() {
    const currentUserId = document.body.getAttribute('data-current-user-id');
    if (!currentUserId) return;
    
    const userRow = document.querySelector(`[data-user-id="${currentUserId}"]`);
    if (userRow) {
        userRow.classList.add('current-user');
        
        // Scroll to user's position if not in top 10
        const userPosition = parseInt(userRow.querySelector('.position').textContent);
        if (userPosition > 10) {
            setTimeout(() => {
                userRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 1000);
        }
    }
}

// Initialize animations
function initAnimations() {
    // Animate rank badges
    const rankBadges = document.querySelectorAll('.rank-badge');
    rankBadges.forEach((badge, index) => {
        badge.style.animation = `pulse 2s ease-in-out ${index * 0.2}s infinite`;
    });
    
    // Animate score counters
    const scoreElements = document.querySelectorAll('.score-value');
    scoreElements.forEach(element => {
        animateScore(element);
    });
    
    // Add trophy animations for top 3
    const topThree = document.querySelectorAll('.leaderboard-table tbody tr:nth-child(-n+3)');
    topThree.forEach((row, index) => {
        const trophy = row.querySelector('.trophy-icon');
        if (trophy) {
            trophy.style.animation = `trophy-glow 3s ease-in-out ${index * 0.5}s infinite`;
        }
    });
}

// Initialize refresh button
function initRefreshButton() {
    const refreshBtn = document.getElementById('refresh-leaderboard');
    if (!refreshBtn) return;
    
    refreshBtn.addEventListener('click', function() {
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...';
        
        refreshLeaderboard().finally(() => {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-sync-alt me-2"></i>Refresh';
        });
    });
}

// Apply leaderboard filter
function applyLeaderboardFilter(filterType) {
    showLoading();
    
    fetch(`/leaderboard/filter/?type=${filterType}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        updateLeaderboardTable(data.leaderboard);
        hideLoading();
    })
    .catch(error => {
        console.error('Error applying filter:', error);
        hideLoading();
        showError('Failed to update leaderboard');
    });
}

// Filter by subject
function filterBySubject(subjectId) {
    if (!subjectId) {
        // Show all entries
        const rows = document.querySelectorAll('.leaderboard-table tbody tr');
        rows.forEach(row => {
            row.style.display = '';
        });
        return;
    }
    
    showLoading();
    
    fetch(`/leaderboard/subject/${subjectId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        updateLeaderboardTable(data.leaderboard);
        hideLoading();
    })
    .catch(error => {
        console.error('Error filtering by subject:', error);
        hideLoading();
        showError('Failed to filter leaderboard');
    });
}

// Filter by time range
function filterByTimeRange(range) {
    showLoading();
    
    fetch(`/leaderboard/time-range/?range=${range}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        updateLeaderboardTable(data.leaderboard);
        hideLoading();
    })
    .catch(error => {
        console.error('Error filtering by time range:', error);
        hideLoading();
        showError('Failed to filter leaderboard');
    });
}

// Refresh leaderboard
function refreshLeaderboard() {
    return fetch('/leaderboard/refresh/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        updateLeaderboardTable(data.leaderboard);
        showSuccess('Leaderboard updated successfully');
    })
    .catch(error => {
        console.error('Error refreshing leaderboard:', error);
        showError('Failed to refresh leaderboard');
    });
}

// Update leaderboard table
function updateLeaderboardTable(leaderboardData) {
    const tbody = document.querySelector('.leaderboard-table tbody');
    if (!tbody) return;
    
    // Clear existing rows
    tbody.innerHTML = '';
    
    // Add new rows
    leaderboardData.forEach((entry, index) => {
        const row = createLeaderboardRow(entry, index + 1);
        tbody.appendChild(row);
    });
    
    // Reinitialize animations and effects
    initLeaderboardTable();
    initUserHighlight();
}

// Create leaderboard row
function createLeaderboardRow(entry, position) {
    const row = document.createElement('tr');
    row.setAttribute('data-user-id', entry.user_id);
    
    let rankBadge = '';
    if (position === 1) {
        rankBadge = '<i class="fas fa-crown text-warning trophy-icon"></i>';
    } else if (position === 2) {
        rankBadge = '<i class="fas fa-medal text-secondary trophy-icon"></i>';
    } else if (position === 3) {
        rankBadge = '<i class="fas fa-award text-warning trophy-icon"></i>';
    }
    
    row.innerHTML = `
        <td class="position">${rankBadge} ${position}</td>
        <td>
            <div class="d-flex align-items-center">
                <div class="user-avatar me-3">${entry.user_name.charAt(0).toUpperCase()}</div>
                <div>
                    <div class="fw-bold">${entry.user_name}</div>
                    <small class="text-muted">${entry.year_of_study || 'Medical Student'}</small>
                </div>
            </div>
        </td>
        <td class="score-value" data-score="${entry.total_score}">${entry.total_score}</td>
        <td>${entry.quizzes_completed}</td>
        <td>${entry.accuracy}%</td>
        <td>
            <div class="progress" style="height: 8px;">
                <div class="progress-bar bg-success" style="width: ${entry.accuracy}%"></div>
            </div>
        </td>
    `;
    
    return row;
}

// Highlight top performers
function highlightTopPerformers() {
    const topThree = document.querySelectorAll('.leaderboard-table tbody tr:nth-child(-n+3)');
    
    topThree.forEach((row, index) => {
        row.classList.add('top-performer');
        
        switch(index) {
            case 0:
                row.classList.add('rank-1');
                break;
            case 1:
                row.classList.add('rank-2');
                break;
            case 2:
                row.classList.add('rank-3');
                break;
        }
    });
}

// Animate score counting
function animateScore(element) {
    const targetScore = parseInt(element.getAttribute('data-score'));
    const duration = 2000;
    const startTime = performance.now();
    
    function updateScore(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const currentScore = Math.floor(targetScore * easeOutCubic);
        
        element.textContent = currentScore.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(updateScore);
        } else {
            element.textContent = targetScore.toLocaleString();
        }
    }
    
    requestAnimationFrame(updateScore);
}

// Show loading state
function showLoading() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'leaderboard-loading';
    loadingOverlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="mt-2">Updating leaderboard...</div>
        </div>
    `;
    
    const container = document.querySelector('.leaderboard-container');
    if (container) {
        container.appendChild(loadingOverlay);
    }
}

// Hide loading state
function hideLoading() {
    const loadingOverlay = document.querySelector('.leaderboard-loading');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Show success message
function showSuccess(message) {
    showMessage(message, 'success');
}

// Show error message
function showError(message) {
    showMessage(message, 'danger');
}

// Show message
function showMessage(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.leaderboard-container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Search functionality
function initLeaderboardSearch() {
    const searchInput = document.getElementById('leaderboard-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = document.querySelectorAll('.leaderboard-table tbody tr');
        
        rows.forEach(row => {
            const userName = row.querySelector('.fw-bold').textContent.toLowerCase();
            
            if (userName.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Export leaderboard data
function exportLeaderboard(format = 'csv') {
    const data = collectLeaderboardData();
    
    if (format === 'csv') {
        downloadCSV(data);
    } else if (format === 'json') {
        downloadJSON(data);
    }
}

// Collect leaderboard data
function collectLeaderboardData() {
    const rows = document.querySelectorAll('.leaderboard-table tbody tr');
    const data = [];
    
    rows.forEach(row => {
        const position = row.querySelector('.position').textContent.trim();
        const name = row.querySelector('.fw-bold').textContent;
        const score = row.querySelector('.score-value').textContent;
        const quizzes = row.cells[3].textContent;
        const accuracy = row.cells[4].textContent;
        
        data.push({
            position: position,
            name: name,
            score: score,
            quizzes_completed: quizzes,
            accuracy: accuracy
        });
    });
    
    return data;
}

// Download as CSV
function downloadCSV(data) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `leaderboard_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    
    window.URL.revokeObjectURL(url);
}

// Download as JSON
function downloadJSON(data) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `leaderboard_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    
    window.URL.revokeObjectURL(url);
}

// Convert data to CSV format
function convertToCSV(data) {
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');
    
    return csvContent;
}

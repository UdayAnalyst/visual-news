document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const newsCard = document.getElementById('newsCard');
    const passBtn = document.getElementById('passBtn');
    const likeBtn = document.getElementById('likeBtn');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const likedCount = document.getElementById('likedCount');
    const passedCount = document.getElementById('passedCount');
    const preferencesBtn = document.getElementById('preferencesBtn');
    const savePreferencesBtn = document.getElementById('savePreferences');
    const refreshNewsBtn = document.getElementById('refreshNews');
    const preferencesModal = new bootstrap.Modal(document.getElementById('preferencesModal'));
    const noMoreModal = new bootstrap.Modal(document.getElementById('noMoreModal'));

    // State
    let currentNews = [];
    let currentIndex = 0;
    let likedTopics = {};
    let passedTopics = {};
    let userPreferences = []; // Will be loaded from server
    let isAnimating = false;
    let userEngagements = {}; // Track user's article engagements

    // Initialize
    loadUserPreferences().then(() => {
        loadNews();
    });

    // Event Listeners
    passBtn.addEventListener('click', () => swipeNews('pass'));
    likeBtn.addEventListener('click', () => swipeNews('like'));
    prevBtn.addEventListener('click', showPreviousNews);
    nextBtn.addEventListener('click', showNextNews);
    preferencesBtn.addEventListener('click', () => preferencesModal.show());
    savePreferencesBtn.addEventListener('click', savePreferences);
    refreshNewsBtn.addEventListener('click', () => {
        noMoreModal.hide();
        loadNews();
    });

    // Touch events for mobile swiping
    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let currentY = 0;
    let isDragging = false;

    newsCard.addEventListener('touchstart', handleTouchStart, { passive: false });
    newsCard.addEventListener('touchmove', handleTouchMove, { passive: false });
    newsCard.addEventListener('touchend', handleTouchEnd, { passive: false });

    // Mouse events for desktop
    newsCard.addEventListener('mousedown', handleMouseDown);
    newsCard.addEventListener('mousemove', handleMouseMove);
    newsCard.addEventListener('mouseup', handleMouseUp);
    newsCard.addEventListener('mouseleave', handleMouseUp);

    function handleTouchStart(e) {
        if (isAnimating) return;
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isDragging = true;
        newsCard.style.transition = 'none';
    }

    function handleTouchMove(e) {
        if (!isDragging || isAnimating) return;
        e.preventDefault();
        currentX = e.touches[0].clientX;
        currentY = e.touches[0].clientY;
        const deltaX = currentX - startX;
        const deltaY = currentY - startY;
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            newsCard.style.transform = `translateX(${deltaX}px) rotate(${deltaX * 0.1}deg)`;
            newsCard.style.opacity = Math.max(0.3, 1 - Math.abs(deltaX) / 200);
        }
    }

    function handleTouchEnd(e) {
        if (!isDragging || isAnimating) return;
        isDragging = false;
        const deltaX = currentX - startX;
        
        if (Math.abs(deltaX) > 100) {
            if (deltaX > 0) {
                swipeNews('like');
            } else {
                swipeNews('pass');
            }
        } else {
            resetCardPosition();
        }
    }

    function handleMouseDown(e) {
        if (isAnimating) return;
        startX = e.clientX;
        startY = e.clientY;
        isDragging = true;
        newsCard.style.transition = 'none';
        e.preventDefault();
    }

    function handleMouseMove(e) {
        if (!isDragging || isAnimating) return;
        currentX = e.clientX;
        currentY = e.clientY;
        const deltaX = currentX - startX;
        const deltaY = currentY - startY;
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            newsCard.style.transform = `translateX(${deltaX}px) rotate(${deltaX * 0.1}deg)`;
            newsCard.style.opacity = Math.max(0.3, 1 - Math.abs(deltaX) / 200);
        }
    }

    function handleMouseUp(e) {
        if (!isDragging || isAnimating) return;
        isDragging = false;
        const deltaX = currentX - startX;
        
        if (Math.abs(deltaX) > 100) {
            if (deltaX > 0) {
                swipeNews('like');
            } else {
                swipeNews('pass');
            }
        } else {
            resetCardPosition();
        }
    }

    function resetCardPosition() {
        newsCard.style.transition = 'all 0.3s ease';
        newsCard.style.transform = 'translateX(0) rotate(0)';
        newsCard.style.opacity = '1';
    }

    function loadUserPreferences() {
        // Load from server
        return fetch('/api/user-preferences')
            .then(response => response.json())
            .then(data => {
                userPreferences = data.preferences || [];
                updatePreferencesUI();
            })
            .catch(error => {
                console.error('Error loading user preferences:', error);
                // Fallback to empty array if server fails
                userPreferences = [];
                updatePreferencesUI();
            });
    }

    function savePreferences() {
        const checkboxes = document.querySelectorAll('.topic-checkbox:checked');
        const newPreferences = Array.from(checkboxes).map(cb => cb.value);
        
        if (newPreferences.length === 0) {
            alert('Please select at least one topic of interest.');
            return;
        }
        
        // Save to server
        fetch('/api/user-preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                preferences: newPreferences
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                userPreferences = newPreferences;
                preferencesModal.hide();
                loadNews();
            } else {
                alert('Error saving preferences: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error saving preferences:', error);
            alert('Error saving preferences. Please try again.');
        });
    }

    function updatePreferencesUI() {
        document.querySelectorAll('.topic-checkbox').forEach(checkbox => {
            checkbox.checked = userPreferences.includes(checkbox.value);
        });
    }

    function loadNews() {
        if (userPreferences.length === 0) {
            showNoNews();
            return;
        }

        const topicParams = userPreferences.map(topic => `topics=${topic}`).join('&');
        
        fetch(`/api/news?${topicParams}&num_articles=20`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0 || data[0].error) {
                    showNoNews();
                    return;
                }
                currentNews = data;
                currentIndex = 0;
                displayCurrentNews();
                updateNavigationButtons();
            })
            .catch(error => {
                console.error('Error loading news:', error);
                showError('Failed to load news. Please try again.');
            });
    }

    function displayCurrentNews() {
        if (currentIndex >= currentNews.length) {
            showNoMoreNews();
            return;
        }

        const article = currentNews[currentIndex];
        const topicConfig = getTopicConfig(article.topic);
        const articleId = article.id || `${article.title}_${article.published_at}`;
        const userEngagement = userEngagements[articleId] || { liked: false, disliked: false };
        
        newsCard.innerHTML = `
            <div class="card-content">
                <div class="news-image">
                    <img src="${article.image_url || getDefaultImage(article.topic)}" alt="${article.title}" 
                         onload="handleImageLoad(this)" 
                         onerror="handleImageError(this)"
                         style="opacity: 0; transition: opacity 0.3s ease;">
                    ${article.likes > 0 ? `
                        <div class="popularity-badge">
                            <i class="fas fa-fire"></i>
                            ${article.likes} likes
                        </div>
                    ` : ''}
                </div>
                <div class="news-body">
                    <div class="news-meta">
                        <span class="topic-badge ${topicConfig.color.replace('text-', 'bg-')}">
                            <i class="${topicConfig.icon} me-1"></i>
                            ${topicConfig.name}
                        </span>
                        <span class="text-muted">
                            <i class="fas fa-calendar-alt me-1"></i>
                            ${article.published_at}
                        </span>
                    </div>
                    <h3 class="news-title">${article.title}</h3>
                    <div class="quick-notes">
                        <h6><i class="fas fa-sticky-note"></i> Quick Notes</h6>
                        <p>${article.summary}</p>
                    </div>
                    <div class="news-description">
                        ${article.description}
                    </div>
                    ${article.url ? `
                        <a href="${article.url}" target="_blank" class="read-more">
                            <i class="fas fa-external-link-alt me-2"></i>
                            Read Full Article
                        </a>
                    ` : ''}
                </div>
                <div class="article-engagement">
                    <div class="engagement-stats">
                        <div class="engagement-stat">
                            <i class="fas fa-heart"></i>
                            <span>${article.likes || 0}</span>
                        </div>
                        <div class="engagement-stat">
                            <i class="fas fa-thumbs-down"></i>
                            <span>${article.dislikes || 0}</span>
                        </div>
                        <div class="engagement-stat">
                            <i class="fas fa-eye"></i>
                            <span>${article.views || 0}</span>
                        </div>
                    </div>
                    <div class="engagement-buttons">
                        <button class="engagement-btn like-btn ${userEngagement.liked ? 'active' : ''}" 
                                data-article-id="${articleId}" 
                                onclick="handleArticleEngagement('${articleId}', 'like')">
                            <i class="fas fa-heart"></i>
                        </button>
                        <button class="engagement-btn dislike-btn ${userEngagement.disliked ? 'active' : ''}" 
                                data-article-id="${articleId}" 
                                onclick="handleArticleEngagement('${articleId}', 'dislike')">
                            <i class="fas fa-thumbs-down"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        newsCard.classList.add('new-card');
        setTimeout(() => newsCard.classList.remove('new-card'), 500);
    }

    function handleImageLoad(img) {
        img.style.opacity = '1';
    }

    function handleImageError(img) {
        console.log('Image failed to load, using fallback');
        // Create a simple colored placeholder based on topic
        const article = currentNews[currentIndex];
        const topicConfig = getTopicConfig(article.topic);
        const color = topicConfig.color.replace('text-', '').replace('danger', 'dc3545').replace('primary', '007bff').replace('warning', 'ffc107').replace('success', '28a745').replace('info', '17a2b8').replace('purple', '6f42c1').replace('orange', 'fd7e14').replace('green', '20c997');
        
        img.src = `data:image/svg+xml;charset=utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="100%" height="100%" fill="%23${color}"/><text x="50%" y="50%" font-family="Arial" font-size="24" fill="white" text-anchor="middle" dy=".3em">${topicConfig.name}</text></svg>`;
        img.style.opacity = '1';
    }

    function handleArticleEngagement(articleId, action) {
        const button = document.querySelector(`[data-article-id="${articleId}"].${action}-btn`);
        const isActive = button.classList.contains('active');
        
        // Toggle engagement
        if (isActive) {
            // Remove engagement
            button.classList.remove('active');
            userEngagements[articleId] = {
                ...userEngagements[articleId],
                [action]: false
            };
        } else {
            // Add engagement
            button.classList.add('active');
            userEngagements[articleId] = {
                ...userEngagements[articleId],
                [action]: true
            };
            
            // Remove opposite engagement if exists
            const oppositeAction = action === 'like' ? 'dislike' : 'like';
            const oppositeButton = document.querySelector(`[data-article-id="${articleId}"].${oppositeAction}-btn`);
            if (oppositeButton.classList.contains('active')) {
                oppositeButton.classList.remove('active');
                userEngagements[articleId][oppositeAction] = false;
            }
        }
        
        // Add pulse animation
        button.classList.add('pulse');
        setTimeout(() => button.classList.remove('pulse'), 300);
        
        // Send to server
        fetch('/api/article-engagement', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                article_id: articleId,
                action: action,
                is_active: !isActive
            })
        }).catch(error => console.error('Error updating engagement:', error));
    }

    function swipeNews(action) {
        if (isAnimating || currentIndex >= currentNews.length) return;
        
        isAnimating = true;
        const article = currentNews[currentIndex];
        const topic = article.topic;
        
        // Update statistics
        if (action === 'like') {
            likedCount.textContent = parseInt(likedCount.textContent) + 1;
            likedTopics[topic] = (likedTopics[topic] || 0) + 1;
            showSwipeFeedback('like');
        } else {
            passedCount.textContent = parseInt(passedCount.textContent) + 1;
            passedTopics[topic] = (passedTopics[topic] || 0) + 1;
            showSwipeFeedback('pass');
        }

        // Animate card out
        newsCard.style.transition = 'all 0.5s ease';
        if (action === 'like') {
            newsCard.style.transform = 'translateX(100vw) rotate(30deg)';
        } else {
            newsCard.style.transform = 'translateX(-100vw) rotate(-30deg)';
        }
        newsCard.style.opacity = '0';

        // Move to next news after animation
        setTimeout(() => {
            currentIndex++;
            if (currentIndex < currentNews.length) {
                displayCurrentNews();
                resetCardPosition();
            } else {
                showNoMoreNews();
            }
            updateNavigationButtons();
            isAnimating = false;
        }, 500);
    }

    function showSwipeFeedback(action) {
        const feedback = document.createElement('div');
        feedback.className = `swipe-feedback ${action}`;
        feedback.innerHTML = action === 'like' ? '❤️ LIKED!' : '👎 PASSED';
        newsCard.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 1000);
    }

    function showPreviousNews() {
        if (currentIndex > 0 && !isAnimating) {
            currentIndex--;
            displayCurrentNews();
            updateNavigationButtons();
        }
    }

    function showNextNews() {
        if (currentIndex < currentNews.length - 1 && !isAnimating) {
            currentIndex++;
            displayCurrentNews();
            updateNavigationButtons();
        }
    }

    function updateNavigationButtons() {
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex >= currentNews.length - 1;
    }

    function showNoNews() {
        newsCard.innerHTML = `
            <div class="card-content">
                <div class="news-body text-center py-5">
                    <i class="fas fa-newspaper fa-3x text-muted mb-3"></i>
                    <h4>No News Available</h4>
                    <p>Please select some topics in preferences to see news.</p>
                    <button class="btn btn-primary" onclick="preferencesModal.show()">
                        <i class="fas fa-cog me-2"></i>
                        Open Preferences
                    </button>
                </div>
            </div>
        `;
    }

    function showNoMoreNews() {
        noMoreModal.show();
    }

    function showError(message) {
        newsCard.innerHTML = `
            <div class="card-content">
                <div class="news-body text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger mb-3"></i>
                    <h4>Error</h4>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="loadNews()">
                        <i class="fas fa-refresh me-2"></i>
                        Try Again
                    </button>
                </div>
            </div>
        `;
    }

    function getTopicConfig(topic) {
        const configs = {
            'inflation': { icon: 'fas fa-chart-line', color: 'text-danger', name: 'Inflation & Economy' },
            'technology': { icon: 'fas fa-microchip', color: 'text-primary', name: 'Technology' },
            'politics': { icon: 'fas fa-landmark', color: 'text-warning', name: 'Politics' },
            'health': { icon: 'fas fa-heartbeat', color: 'text-success', name: 'Health & Medicine' },
            'business': { icon: 'fas fa-briefcase', color: 'text-info', name: 'Business' },
            'science': { icon: 'fas fa-flask', color: 'text-purple', name: 'Science' },
            'sports': { icon: 'fas fa-football-ball', color: 'text-orange', name: 'Sports' },
            'environment': { icon: 'fas fa-leaf', color: 'text-green', name: 'Environment' }
        };
        return configs[topic] || configs['inflation'];
    }

    function getDefaultImage(topic) {
        const topicConfig = getTopicConfig(topic);
        const color = topicConfig.color.replace('text-', '').replace('danger', 'dc3545').replace('primary', '007bff').replace('warning', 'ffc107').replace('success', '28a745').replace('info', '17a2b8').replace('purple', '6f42c1').replace('orange', 'fd7e14').replace('green', '20c997');
        return `data:image/svg+xml;charset=utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="100%" height="100%" fill="%23${color}"/><text x="50%" y="50%" font-family="Arial" font-size="24" fill="white" text-anchor="middle" dy=".3em">${topicConfig.name}</text></svg>`;
    }

    // Global functions
    function selectAllTopics() {
        document.querySelectorAll('.topic-checkbox').forEach(checkbox => {
            checkbox.checked = true;
        });
    }

    function selectNoTopics() {
        document.querySelectorAll('.topic-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });
    }

    // Make functions globally available
    window.handleArticleEngagement = handleArticleEngagement;
    window.preferencesModal = preferencesModal;
    window.loadNews = loadNews;
    window.handleImageLoad = handleImageLoad;
    window.handleImageError = handleImageError;
    window.selectAllTopics = selectAllTopics;
    window.selectNoTopics = selectNoTopics;
});

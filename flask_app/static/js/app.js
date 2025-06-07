// Degrees of Spotify - Frontend JavaScript

class DegreesOfSpotify {
    constructor() {
        this.currentSearchId = null;
        this.searchInterval = null;
        this.suggestionTimeouts = {};
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadDatabaseStats();
        this.initCursorGradient();
    }
    
    bindEvents() {
        // Search form submission
        document.getElementById('searchForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startSearch();
        });
        
        // Artist input suggestions
        this.setupArtistSuggestions('artist1', 'artist1Suggestions');
        this.setupArtistSuggestions('artist2', 'artist2Suggestions');
        
        // Keypress animations for artist input boxes
        this.setupKeypressAnimations();
        
        // Clear suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-group')) {
                this.hideSuggestions('artist1Suggestions');
                this.hideSuggestions('artist2Suggestions');
            }
        });
    }
    
    setupArtistSuggestions(inputId, suggestionsId) {
        // Suggestions functionality disabled
        // This method is kept for compatibility but does nothing
        return;
    }
    
    setupKeypressAnimations() {
        // Add keypress animations to artist input fields
        const artistInputs = ['artist1', 'artist2'];
        
        artistInputs.forEach(inputId => {
            const input = document.getElementById(inputId);
            const inputGroup = input.closest('.input-group');
            
            if (input && inputGroup) {
                input.addEventListener('keydown', (e) => {
                    // Only animate for actual character keys, not special keys
                    if (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Delete') {
                        this.triggerKeypressAnimation(inputGroup);
                    }
                });
            }
        });
    }
    
    triggerKeypressAnimation(inputGroup) {
        const input = inputGroup.querySelector('.form-control');
        const isInputFocused = document.activeElement === input;
        const isHovered = inputGroup.matches(':hover');
        
        // Determine which animation to use based on state
        const animationClass = (isInputFocused || isHovered) ? 'keypress-from-hover' : 'keypress-animate';
        const duration = (isInputFocused || isHovered) ? 150 : 200;
        
        // Remove existing animation classes if present
        inputGroup.classList.remove('keypress-animate', 'keypress-from-hover');
        
        // Force reflow to ensure the class removal takes effect
        inputGroup.offsetHeight;
        
        // Add appropriate animation class
        inputGroup.classList.add(animationClass);
        
        // Remove animation class after animation completes
        setTimeout(() => {
            inputGroup.classList.remove(animationClass);
        }, duration);
    }
    
    async fetchArtistSuggestions(query, suggestionsDiv, input) {
        // Suggestions functionality disabled
        return;
    }
    
    displaySuggestions(artists, suggestionsDiv, input) {
        // Suggestions functionality disabled
        return;
    }
    
    hideSuggestions(suggestionsId) {
        // Suggestions functionality disabled
        return;
    }
    
    async startSearch() {
        const artist1 = document.getElementById('artist1').value.trim();
        const artist2 = document.getElementById('artist2').value.trim();
        const algorithm = document.getElementById('algorithm').value;
        
        if (!artist1 || !artist2) {
            this.showAlert('Please enter both artist names.', 'danger');
            return;
        }
        
        if (artist1.toLowerCase() === artist2.toLowerCase()) {
            this.showAlert('Please enter two different artists.', 'warning');
            return;
        }
        
        // Hide previous results and show progress
        this.hideResults();
        this.showProgress();
        this.disableSearchForm(true);
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    artist1: artist1,
                    artist2: artist2,
                    algorithm: algorithm
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentSearchId = data.search_id;
                this.pollSearchStatus();
            } else {
                throw new Error(data.error || 'Failed to start search');
            }
        } catch (error) {
            console.error('Error starting search:', error);
            this.showAlert(`Error starting search: ${error.message}`, 'danger');
            this.hideProgress();
            this.disableSearchForm(false);
        }
    }
    
    async pollSearchStatus() {
        if (!this.currentSearchId) return;
        
        this.searchInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/search/${this.currentSearchId}/status`);
                const data = await response.json();
                
                if (response.ok) {
                    this.updateProgress(data.progress, data.message);
                    
                    if (data.status === 'completed') {
                        clearInterval(this.searchInterval);
                        await this.fetchSearchResult();
                    } else if (data.status === 'failed') {
                        clearInterval(this.searchInterval);
                        this.showAlert(`Search failed: ${data.error || 'Unknown error'}`, 'danger');
                        this.hideProgress();
                        this.disableSearchForm(false);
                    }
                } else {
                    throw new Error(data.error || 'Failed to get search status');
                }
            } catch (error) {
                console.error('Error polling search status:', error);
                clearInterval(this.searchInterval);
                this.showAlert(`Error checking search status: ${error.message}`, 'danger');
                this.hideProgress();
                this.disableSearchForm(false);
            }
        }, 1000); // Poll every second
    }
    
    async fetchSearchResult() {
        try {
            const response = await fetch(`/api/search/${this.currentSearchId}/result`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayResults(data.result);
            } else {
                throw new Error(data.error || 'Failed to get search result');
            }
        } catch (error) {
            console.error('Error fetching search result:', error);
            this.showAlert(`Error getting search result: ${error.message}`, 'danger');
        } finally {
            this.hideProgress();
            this.disableSearchForm(false);
            this.currentSearchId = null;
        }
    }
    
    displayResults(result) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsTitle = document.getElementById('resultsTitle');
        const resultsContent = document.getElementById('resultsContent');
        
        if (result.found) {
            resultsTitle.innerHTML = `<i class="fas fa-check-circle text-success"></i> Connection Found!`;
            
            let pathHtml = `
                <div class="alert alert-success">
                    <h5><i class="fas fa-route"></i> Path Found</h5>
                    <p><strong>${result.degrees}</strong> degrees of separation between 
                       <strong>${result.start_artist}</strong> and <strong>${result.end_artist}</strong></p>
                    <p><small>Algorithm: ${result.algorithm} | Artists searched: ${result.artists_searched}</small></p>
                </div>
                
                <div class="path-container">
                    <h6 class="text-center mb-3">Connection Path:</h6>
            `;
            
            result.path_names.forEach((artist, index) => {
                pathHtml += `
                    <div class="path-step">
                        <div class="step-number">${index + 1}</div>
                        <div class="step-content">
                            <p class="artist-name">${artist}</p>
                        </div>
                    </div>
                `;
                
                if (index < result.path_names.length - 1) {
                    pathHtml += '<div class="connection-arrow"><i class="fas fa-arrow-down"></i></div>';
                }
            });
            
            pathHtml += '</div>';
            resultsContent.innerHTML = pathHtml;
        } else {
            resultsTitle.innerHTML = `<i class="fas fa-times-circle text-danger"></i> No Connection Found`;
            resultsContent.innerHTML = `
                <div class="alert alert-warning">
                    <h5><i class="fas fa-exclamation-triangle"></i> No Path Found</h5>
                    <p>No connection was found between <strong>${result.start_artist}</strong> 
                       and <strong>${result.end_artist}</strong> in our current database.</p>
                    <p><small>Algorithm: ${result.algorithm}</small></p>
                </div>
                <div class="text-center">
                    <p class="text-muted">Try searching for artists with more collaborations, or check back later as our database grows!</p>
                </div>
            `;
        }
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        // Refresh database stats
        this.loadDatabaseStats();
    }
    
    showProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'block';
        this.updateProgress(0, 'Initializing search...');
    }
    
    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'none';
    }
    
    updateProgress(percentage, message) {
        const progressBar = document.getElementById('progressBar');
        const progressMessage = document.getElementById('progressMessage');
        
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = '';
        progressMessage.textContent = message;
        
        if (percentage >= 100) {
            progressBar.classList.remove('progress-bar-animated');
        }
    }
    
    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.display = 'none';
    }
    
    disableSearchForm(disabled) {
        const searchBtn = document.getElementById('searchBtn');
        const inputs = document.querySelectorAll('#searchForm input, #searchForm select');
        
        inputs.forEach(input => input.disabled = disabled);
        searchBtn.disabled = disabled;
        
        if (disabled) {
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
        } else {
            searchBtn.innerHTML = '<i class="fas fa-search"></i> Find Connection';
        }
    }
    
    async loadDatabaseStats() {
        // Database stats section has been removed from the UI
        // This method is kept for compatibility but does nothing
    }
    
    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-dismissible');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const searchForm = document.getElementById('searchForm');
        searchForm.insertAdjacentHTML('beforebegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert-dismissible');
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
    
    initCursorGradient() {
        // Create the cursor gradient element
        const cursorGradient = document.createElement('div');
        cursorGradient.className = 'cursor-gradient';
        document.body.appendChild(cursorGradient);
        
        let mouseX = 0;
        let mouseY = 0;
        let currentX = 0;
        let currentY = 0;
        let isMouseMoving = false;
        let fadeTimeout;
        let animationId;
        
        // Smooth animation function
        const animate = () => {
            // Lerp (linear interpolation) for smooth movement
            const ease = 0.15;
            currentX += (mouseX - currentX) * ease;
            currentY += (mouseY - currentY) * ease;
            
            // Update gradient position
            cursorGradient.style.left = currentX + 'px';
            cursorGradient.style.top = currentY + 'px';
            
            animationId = requestAnimationFrame(animate);
        };
        
        // Start animation loop
        animate();
        
        // Track mouse movement
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            
            // Show gradient when mouse moves
            if (!isMouseMoving) {
                isMouseMoving = true;
                cursorGradient.classList.add('active');
            }
            
            // Clear existing timeout
            clearTimeout(fadeTimeout);
            
            // Set timeout to fade out gradient when mouse stops moving
            fadeTimeout = setTimeout(() => {
                isMouseMoving = false;
                cursorGradient.classList.remove('active');
            }, 3000); // Fade out after 3 seconds of no movement
        });
        
        // Hide gradient when mouse leaves the window
        document.addEventListener('mouseleave', () => {
            cursorGradient.classList.remove('active');
            isMouseMoving = false;
            clearTimeout(fadeTimeout);
        });
        
        // Show gradient when mouse enters the window
        document.addEventListener('mouseenter', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            cursorGradient.classList.add('active');
            isMouseMoving = true;
        });
        
        // Cleanup function
        window.addEventListener('beforeunload', () => {
            cancelAnimationFrame(animationId);
        });
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DegreesOfSpotify();
});
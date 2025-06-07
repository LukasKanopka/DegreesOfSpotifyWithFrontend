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
        
        // Clear suggestions when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-group')) {
                this.hideSuggestions('artist1Suggestions');
                this.hideSuggestions('artist2Suggestions');
            }
        });
    }
    
    setupArtistSuggestions(inputId, suggestionsId) {
        const input = document.getElementById(inputId);
        const suggestionsDiv = document.getElementById(suggestionsId);
        
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            
            // Clear previous timeout
            if (this.suggestionTimeouts[inputId]) {
                clearTimeout(this.suggestionTimeouts[inputId]);
            }
            
            if (query.length < 2) {
                this.hideSuggestions(suggestionsId);
                return;
            }
            
            // Debounce the API call
            this.suggestionTimeouts[inputId] = setTimeout(() => {
                this.fetchArtistSuggestions(query, suggestionsDiv, input);
            }, 300);
        });
        
        input.addEventListener('focus', () => {
            if (input.value.length >= 2) {
                suggestionsDiv.style.display = 'block';
            }
        });
    }
    
    async fetchArtistSuggestions(query, suggestionsDiv, input) {
        try {
            const response = await fetch(`/api/artists/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.artists && data.artists.length > 0) {
                this.displaySuggestions(data.artists, suggestionsDiv, input);
            } else {
                this.hideSuggestions(suggestionsDiv.id);
            }
        } catch (error) {
            console.error('Error fetching artist suggestions:', error);
            this.hideSuggestions(suggestionsDiv.id);
        }
    }
    
    displaySuggestions(artists, suggestionsDiv, input) {
        suggestionsDiv.innerHTML = '';
        
        artists.forEach(artist => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            
            item.innerHTML = `
                ${artist.image ? `<img src="${artist.image}" alt="${artist.name}" class="suggestion-image">` : ''}
                <div class="suggestion-info">
                    <p class="suggestion-name">${artist.name}</p>
                    <p class="suggestion-details">${artist.followers.toLocaleString()} followers</p>
                </div>
            `;
            
            item.addEventListener('click', () => {
                input.value = artist.name;
                this.hideSuggestions(suggestionsDiv.id);
            });
            
            suggestionsDiv.appendChild(item);
        });
        
        suggestionsDiv.style.display = 'block';
    }
    
    hideSuggestions(suggestionsId) {
        const suggestionsDiv = document.getElementById(suggestionsId);
        if (suggestionsDiv) {
            suggestionsDiv.style.display = 'none';
        }
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
        document.getElementById('progressSection').style.display = 'block';
        this.updateProgress(0, 'Initializing search...');
    }
    
    hideProgress() {
        document.getElementById('progressSection').style.display = 'none';
    }
    
    updateProgress(percentage, message) {
        const progressBar = document.getElementById('progressBar');
        const progressMessage = document.getElementById('progressMessage');
        
        progressBar.style.width = `${percentage}%`;
        progressBar.textContent = `${percentage}%`;
        progressMessage.textContent = message;
        
        if (percentage >= 100) {
            progressBar.classList.remove('progress-bar-animated');
        }
    }
    
    hideResults() {
        document.getElementById('resultsSection').style.display = 'none';
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
        try {
            // For now, we'll use placeholder stats since we don't have a stats endpoint yet
            // This can be implemented later when the backend is fully set up
            document.getElementById('totalArtists').textContent = '-';
            document.getElementById('totalConnections').textContent = '-';
            document.getElementById('avgConnections').textContent = '-';
        } catch (error) {
            console.error('Error loading database stats:', error);
        }
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
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DegreesOfSpotify();
});
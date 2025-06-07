import os
import uuid
import threading
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime

from services.spotify_service import SpotifyService
from services.graph_service import GraphService
from services.search_service import SearchService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize services
spotify_service = SpotifyService()
graph_service = GraphService()
search_service = SearchService(spotify_service, graph_service)

# Store for active searches
active_searches = {}

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def start_search():
    """
    Initiate artist connection search.
    
    Expected JSON payload:
    {
        "artist1": "Artist Name 1",
        "artist2": "Artist Name 2", 
        "algorithm": "bfs" or "dfs"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        artist1 = data.get('artist1', '').strip()
        artist2 = data.get('artist2', '').strip()
        algorithm = data.get('algorithm', 'bfs').lower()
        
        if not artist1 or not artist2:
            return jsonify({'error': 'Both artist names are required'}), 400
            
        if algorithm not in ['bfs', 'dfs']:
            return jsonify({'error': 'Algorithm must be "bfs" or "dfs"'}), 400
        
        # Generate unique search ID
        search_id = str(uuid.uuid4())
        
        # Initialize search status
        active_searches[search_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing search...',
            'result': None,
            'error': None,
            'started_at': datetime.now().isoformat(),
            'artist1': artist1,
            'artist2': artist2,
            'algorithm': algorithm
        }
        
        # Start search in background thread
        thread = threading.Thread(
            target=_run_search,
            args=(search_id, artist1, artist2, algorithm)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'search_id': search_id,
            'status': 'started',
            'message': 'Search initiated successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting search: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/search/<search_id>/status', methods=['GET'])
def get_search_status(search_id):
    """Get search progress and status."""
    try:
        if search_id not in active_searches:
            return jsonify({'error': 'Search not found'}), 404
            
        search_data = active_searches[search_id]
        
        return jsonify({
            'search_id': search_id,
            'status': search_data['status'],
            'progress': search_data['progress'],
            'message': search_data['message'],
            'started_at': search_data['started_at'],
            'artist1': search_data['artist1'],
            'artist2': search_data['artist2'],
            'algorithm': search_data['algorithm'],
            'error': search_data.get('error')
        })
        
    except Exception as e:
        logger.error(f"Error getting search status: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/search/<search_id>/result', methods=['GET'])
def get_search_result(search_id):
    """Get search results."""
    try:
        if search_id not in active_searches:
            return jsonify({'error': 'Search not found'}), 404
            
        search_data = active_searches[search_id]
        
        if search_data['status'] != 'completed':
            return jsonify({
                'error': 'Search not completed yet',
                'status': search_data['status']
            }), 400
            
        return jsonify({
            'search_id': search_id,
            'status': search_data['status'],
            'result': search_data['result'],
            'started_at': search_data['started_at'],
            'completed_at': search_data.get('completed_at'),
            'artist1': search_data['artist1'],
            'artist2': search_data['artist2'],
            'algorithm': search_data['algorithm']
        })
        
    except Exception as e:
        logger.error(f"Error getting search result: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/artists/search', methods=['GET'])
def search_artists():
    """Search for artist suggestions."""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
            
        if len(query) < 2:
            return jsonify({'artists': []})
            
        # Get artist suggestions from Spotify
        artists = spotify_service.search_artists(query, limit=10)
        
        return jsonify({'artists': artists})
        
    except Exception as e:
        logger.error(f"Error searching artists: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def _run_search(search_id, artist1, artist2, algorithm):
    """Run the search in a background thread."""
    try:
        # Update status
        active_searches[search_id]['status'] = 'running'
        active_searches[search_id]['message'] = 'Searching for artists...'
        active_searches[search_id]['progress'] = 10
        
        # Run the search
        result = search_service.find_connection(
            artist1, artist2, algorithm, 
            progress_callback=lambda progress, message: _update_search_progress(search_id, progress, message)
        )
        
        if result:
            active_searches[search_id]['status'] = 'completed'
            active_searches[search_id]['progress'] = 100
            active_searches[search_id]['message'] = 'Search completed successfully'
            active_searches[search_id]['result'] = result
            active_searches[search_id]['completed_at'] = datetime.now().isoformat()
        else:
            active_searches[search_id]['status'] = 'completed'
            active_searches[search_id]['progress'] = 100
            active_searches[search_id]['message'] = 'No connection found'
            active_searches[search_id]['result'] = None
            active_searches[search_id]['completed_at'] = datetime.now().isoformat()
            
    except Exception as e:
        logger.error(f"Error in search {search_id}: {str(e)}")
        active_searches[search_id]['status'] = 'failed'
        active_searches[search_id]['error'] = str(e)
        active_searches[search_id]['message'] = f'Search failed: {str(e)}'
        active_searches[search_id]['completed_at'] = datetime.now().isoformat()

def _update_search_progress(search_id, progress, message):
    """Update search progress."""
    if search_id in active_searches:
        active_searches[search_id]['progress'] = progress
        active_searches[search_id]['message'] = message

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
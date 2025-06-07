# Degrees of Spotify - Flask Web Application

A web application that finds the shortest path between any two artists on Spotify using their collaboration network.

## Features

- **Web Interface**: Modern, responsive web UI for easy artist searches
- **RESTful API**: Complete API for programmatic access
- **Real-time Progress**: Live updates during search operations
- **Artist Suggestions**: Auto-complete with artist search
- **Multiple Algorithms**: Support for both BFS (shortest path) and DFS (any path)
- **Preserved Functionality**: All original features from the console application

## Project Structure

```
flask_app/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── run.py               # Application runner script
├── .env                 # Environment variables (Spotify credentials)
├── adjacency_list.csv   # Artist collaboration data
├── services/            # Business logic services
│   ├── __init__.py
│   ├── spotify_service.py    # Spotify API integration
│   ├── graph_service.py      # Graph algorithms (BFS/DFS)
│   └── search_service.py     # Search orchestration
├── models/              # Data models
│   ├── __init__.py
│   └── graph_model.py        # Data structures
├── static/              # Static web assets
│   ├── css/
│   │   └── style.css         # Custom styles
│   ├── js/
│   │   └── app.js           # Frontend JavaScript
│   └── images/              # Image assets
└── templates/           # HTML templates
    └── index.html           # Main web interface
```

## Installation

1. **Install Dependencies**:
   ```bash
   cd flask_app
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   Ensure your `.env` file contains your Spotify API credentials:
   ```
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   ```

3. **Run the Application**:
   ```bash
   python run.py
   ```

   Or directly:
   ```bash
   python app.py
   ```

4. **Access the Application**:
   Open your browser and navigate to: `http://localhost:5000`

## API Endpoints

### Web Interface
- `GET /` - Main web application interface

### Search Operations
- `POST /api/search` - Initiate artist connection search
  ```json
  {
    "artist1": "Artist Name 1",
    "artist2": "Artist Name 2",
    "algorithm": "bfs"
  }
  ```

- `GET /api/search/<search_id>/status` - Get search progress
- `GET /api/search/<search_id>/result` - Get search results

### Artist Operations
- `GET /api/artists/search?q=<query>` - Search for artist suggestions

## Usage Examples

### Web Interface
1. Open `http://localhost:5000` in your browser
2. Enter two artist names in the search form
3. Select your preferred algorithm (BFS for shortest path, DFS for any path)
4. Click "Find Connection" and watch the real-time progress
5. View the results showing the connection path

### API Usage

**Start a Search**:
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"artist1": "Drake", "artist2": "Taylor Swift", "algorithm": "bfs"}'
```

**Check Search Status**:
```bash
curl http://localhost:5000/api/search/<search_id>/status
```

**Get Search Results**:
```bash
curl http://localhost:5000/api/search/<search_id>/result
```

**Search for Artists**:
```bash
curl "http://localhost:5000/api/artists/search?q=drake"
```

## Configuration

The application can be configured through environment variables:

- `CLIENT_ID` - Spotify Client ID (required)
- `CLIENT_SECRET` - Spotify Client Secret (required)
- `FLASK_ENV` - Environment (development/production)
- `FLASK_DEBUG` - Enable debug mode (true/false)
- `CSV_FILE` - Path to adjacency list file (default: adjacency_list.csv)
- `REQUEST_TIMEOUT` - Spotify API timeout (default: 10 seconds)
- `RATE_LIMIT_DELAY` - Delay between requests (default: 0.333 seconds)
- `MAX_RETRIES` - Maximum API retries (default: 3)

## Algorithms

### Breadth-First Search (BFS)
- Finds the **shortest path** between two artists
- Explores all artists at the current degree before moving to the next
- Optimal for finding minimum degrees of separation
- Returns artist names in the path for better readability

### Depth-First Search (DFS)
- Finds **any path** between two artists (not necessarily shortest)
- Explores as far as possible along each branch before backtracking
- Faster for finding any connection
- Returns URLs in the path to avoid excessive API calls

## Data Storage

The application uses a CSV-based adjacency list (`adjacency_list.csv`) to store artist collaboration data:
- Each row represents an artist and their collaborators
- Format: `artist_url,collaborator1_url,collaborator2_url,...`
- Backward compatible with the original console application
- Automatically updated when new artists are searched

## Error Handling

The application includes comprehensive error handling:
- Spotify API rate limiting and retry logic
- Invalid artist name handling
- Network error recovery
- Search timeout protection
- Graceful degradation for missing data

## Performance Features

- **Rate Limiting**: Respects Spotify's 3 requests/second limit
- **Caching**: Uses existing adjacency list data to avoid redundant API calls
- **Async Operations**: Background search processing with progress updates
- **Memory Optimization**: Efficient graph traversal algorithms
- **Request Debouncing**: Optimized artist suggestion requests

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=true
python run.py
```

### Testing the API
Use the included examples or tools like Postman to test the API endpoints.

### Extending the Application
- Add new endpoints in `app.py`
- Implement new services in the `services/` directory
- Add new data models in `models/`
- Extend the frontend in `static/` and `templates/`

## Migration from Console Application

This Flask application preserves all functionality from the original console application:
- Same Spotify API integration with rate limiting
- Identical BFS and DFS algorithms
- Compatible adjacency list CSV format
- Preserved error handling and retry logic

The web interface provides a more user-friendly way to access the same powerful artist connection discovery features.

## Troubleshooting

**Common Issues**:

1. **"Configuration Error"**: Check your `.env` file has valid Spotify credentials
2. **"No artist found"**: Verify artist names are spelled correctly
3. **"Search timeout"**: Try with artists that have more collaborations
4. **"Connection refused"**: Ensure the Flask server is running on port 5000

**Debug Mode**:
Enable debug mode for detailed error messages:
```bash
export FLASK_DEBUG=true
python run.py
```

## License

This project maintains the same license as the original console application.
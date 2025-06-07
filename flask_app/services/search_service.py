import logging
from typing import Optional, Dict, Any, Callable

from .spotify_service import SpotifyService
from .graph_service import GraphService

logger = logging.getLogger(__name__)

class SearchService:
    """
    Service for orchestrating artist connection searches.
    
    Combines Spotify API calls with graph algorithms to find connections
    between artists while providing progress tracking.
    """
    
    def __init__(self, spotify_service: SpotifyService, graph_service: GraphService):
        """
        Initialize search service.
        
        Args:
            spotify_service: Service for Spotify API interactions.
            graph_service: Service for graph operations and algorithms.
        """
        self.spotify_service = spotify_service
        self.graph_service = graph_service
        logger.info("Search service initialized")
    
    def find_connection(self, artist1_name: str, artist2_name: str, algorithm: str = "bfs",
                       progress_callback: Optional[Callable[[int, str], None]] = None) -> Optional[Dict[str, Any]]:
        """
        Find connection between two artists using the specified algorithm.
        
        Args:
            artist1_name (str): Name of the first artist.
            artist2_name (str): Name of the second artist.
            algorithm (str): Algorithm to use ("bfs" or "dfs").
            progress_callback: Optional callback for progress updates.
        
        Returns:
            dict: Search result with path information, or None if no connection found.
        """
        try:
            if progress_callback:
                progress_callback(5, "Looking up artists...")
            
            # Get artist URLs from names
            start_url = self.spotify_service.get_artist_url(artist1_name)
            end_url = self.spotify_service.get_artist_url(artist2_name)
            
            if not start_url:
                error_msg = f"Could not find artist: {artist1_name}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(100, error_msg)
                return None
                
            if not end_url:
                error_msg = f"Could not find artist: {artist2_name}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(100, error_msg)
                return None
            
            if progress_callback:
                progress_callback(15, f"Found both artists, starting {algorithm.upper()} search...")
            
            # Check if we need to fetch related artists for the starting artist
            start_connections = self.graph_service.get_artist_connections(start_url)
            if not start_connections:
                if progress_callback:
                    progress_callback(20, f"Fetching related artists for {artist1_name}...")
                
                # Fetch and store related artists
                related_urls = self.spotify_service.find_related_artists(start_url)
                if related_urls:
                    self.graph_service.add_artist_connections(start_url, related_urls)
                    logger.info(f"Added {len(related_urls)} connections for {artist1_name}")
            
            # Perform the search using the specified algorithm
            if algorithm.lower() == "bfs":
                result = self.graph_service.breadth_first_search(
                    start_url, end_url, progress_callback
                )
            elif algorithm.lower() == "dfs":
                result = self.graph_service.depth_first_search(
                    start_url, end_url, progress_callback
                )
            else:
                error_msg = f"Unknown algorithm: {algorithm}"
                logger.error(error_msg)
                if progress_callback:
                    progress_callback(100, error_msg)
                return None
            
            if result:
                # Parse the result and convert URLs to artist names for better readability
                degrees = result[0]
                artists_searched = result[1]
                path_urls = result[2:]
                
                # Convert URLs to names (for BFS, avoid API calls for DFS due to potentially long paths)
                if algorithm.lower() == "bfs":
                    path_names = []
                    for url in path_urls:
                        name = self.spotify_service.get_artist_name(url)
                        path_names.append(name if name else url)
                else:
                    # For DFS, keep URLs to avoid excessive API calls
                    path_names = path_urls
                
                return {
                    "found": True,
                    "degrees": degrees,
                    "artists_searched": artists_searched,
                    "path_urls": path_urls,
                    "path_names": path_names,
                    "algorithm": algorithm.upper(),
                    "start_artist": artist1_name,
                    "end_artist": artist2_name
                }
            else:
                return {
                    "found": False,
                    "degrees": None,
                    "artists_searched": None,
                    "path_urls": [],
                    "path_names": [],
                    "algorithm": algorithm.upper(),
                    "start_artist": artist1_name,
                    "end_artist": artist2_name,
                    "message": "No connection found between the artists in our database."
                }
                
        except Exception as e:
            error_msg = f"Error during search: {str(e)}"
            logger.error(error_msg)
            if progress_callback:
                progress_callback(100, error_msg)
            return None
    
    def expand_artist_network(self, artist_name: str, 
                            progress_callback: Optional[Callable[[int, str], None]] = None) -> Dict[str, Any]:
        """
        Expand the network by fetching related artists for a given artist.
        
        Args:
            artist_name (str): Name of the artist to expand.
            progress_callback: Optional callback for progress updates.
        
        Returns:
            dict: Result of the expansion operation.
        """
        try:
            if progress_callback:
                progress_callback(10, f"Looking up {artist_name}...")
            
            # Get artist URL
            artist_url = self.spotify_service.get_artist_url(artist_name)
            if not artist_url:
                error_msg = f"Could not find artist: {artist_name}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            
            if progress_callback:
                progress_callback(30, f"Fetching related artists for {artist_name}...")
            
            # Check if already in database
            existing_connections = self.graph_service.get_artist_connections(artist_url)
            if existing_connections:
                return {
                    "success": True,
                    "artist": artist_name,
                    "connections_found": len(existing_connections),
                    "message": f"{artist_name} already in database with {len(existing_connections)} connections"
                }
            
            # Fetch related artists
            related_urls = self.spotify_service.find_related_artists(artist_url)
            
            if progress_callback:
                progress_callback(80, f"Saving {len(related_urls)} connections...")
            
            # Save to database
            if related_urls:
                success = self.graph_service.add_artist_connections(artist_url, related_urls)
                if success:
                    if progress_callback:
                        progress_callback(100, f"Successfully added {len(related_urls)} connections")
                    return {
                        "success": True,
                        "artist": artist_name,
                        "connections_found": len(related_urls),
                        "message": f"Successfully added {len(related_urls)} connections for {artist_name}"
                    }
                else:
                    error_msg = "Failed to save connections to database"
                    return {"success": False, "error": error_msg}
            else:
                return {
                    "success": True,
                    "artist": artist_name,
                    "connections_found": 0,
                    "message": f"No related artists found for {artist_name}"
                }
                
        except Exception as e:
            error_msg = f"Error expanding network for {artist_name}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_artist_info(self, artist_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about an artist.
        
        Args:
            artist_name (str): Name of the artist.
        
        Returns:
            dict: Artist information or None if not found.
        """
        try:
            artist_url = self.spotify_service.get_artist_url(artist_name)
            if not artist_url:
                return None
            
            # Get basic info from Spotify
            artist_info = self.spotify_service.get_artist_info(artist_url)
            if not artist_info:
                return None
            
            # Get connections from our database
            connections = self.graph_service.get_artist_connections(artist_url)
            
            return {
                "name": artist_info.get("name"),
                "url": artist_url,
                "popularity": artist_info.get("popularity", 0),
                "genres": artist_info.get("genres", []),
                "followers": artist_info.get("followers", {}).get("total", 0),
                "image": artist_info["images"][0]["url"] if artist_info.get("images") else None,
                "connections_in_db": len(connections),
                "in_database": len(connections) > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting artist info for {artist_name}: {e}")
            return None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current database.
        
        Returns:
            dict: Database statistics.
        """
        try:
            return self.graph_service.get_graph_stats()
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"total_artists": 0, "total_connections": 0, "average_connections": 0}
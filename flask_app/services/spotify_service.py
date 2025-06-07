import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
from typing import Optional, List, Dict, Any

from config import Config

logger = logging.getLogger(__name__)

class SpotifyService:
    """
    Service for interacting with the Spotify API.
    
    Preserves all existing functionality from the original Spotipy.py implementation
    including rate limiting, error handling, and retry logic.
    """
    
    def __init__(self):
        """Initialize Spotify service with authentication."""
        Config.validate_config()
        
        # Authenticate with Spotify API
        client_credentials_manager = SpotifyClientCredentials(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET
        )
        
        self.sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager,
            requests_timeout=Config.REQUEST_TIMEOUT
        )
        
        logger.info("Spotify service initialized successfully")
    
    def safe_request(self, func, *args, **kwargs):
        """
        Executes a Spotify API request with retry logic, handling rate limits.
        
        Preserves the exact functionality from the original implementation.
        
        Args:
            func: The Spotipy function to call.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        
        Returns:
            The result of the Spotipy API call.
        
        Raises:
            Exception: If all retries fail or rate-limiting persists.
        """
        max_retries = Config.MAX_RETRIES
        delay = Config.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                # Log the request time
                logger.debug("Sending Spotify API request...")
                time.sleep(Config.RATE_LIMIT_DELAY)  # Rate limit: 3 requests per second
                
                # Execute the function
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Error in Spotify API request: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Maximum retries reached. Request failed.")
                    raise
    
    def get_artist_url(self, artist_name: str) -> Optional[str]:
        """
        Gets the Spotify URL for an artist by name.
        
        Args:
            artist_name (str): The name of the artist.
        
        Returns:
            str: Spotify URL for the artist or None if not found.
        """
        try:
            result = self.safe_request(self.sp.search, q=artist_name, type="artist", limit=1)
            if not result["artists"]["items"]:
                logger.info(f"No artist found with name: {artist_name}")
                return None
            return result["artists"]["items"][0]["external_urls"]["spotify"]
        except Exception as e:
            logger.error(f"Error getting artist URL for '{artist_name}': {e}")
            return None
    
    def get_artist_name(self, artist_url: str) -> Optional[str]:
        """
        Retrieves the artist's name from their Spotify URL.
        
        Args:
            artist_url (str): Spotify URL of the artist.
        
        Returns:
            str: Name of the artist, or None if the artist is not found.
        """
        try:
            artist_id = artist_url.split("/")[-1]
            result = self.safe_request(self.sp.artist, artist_id)
            return result["name"] if result else None
        except Exception as e:
            logger.error(f"Error fetching artist name for URL '{artist_url}': {e}")
            return None
    
    def search_artists(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for artists by name and return suggestions.
        
        Args:
            query (str): Search query.
            limit (int): Maximum number of results to return.
        
        Returns:
            list: List of artist dictionaries with name, url, and other info.
        """
        try:
            result = self.safe_request(self.sp.search, q=query, type="artist", limit=limit)
            artists = []
            
            for artist in result["artists"]["items"]:
                artists.append({
                    "name": artist["name"],
                    "url": artist["external_urls"]["spotify"],
                    "id": artist["id"],
                    "popularity": artist.get("popularity", 0),
                    "genres": artist.get("genres", []),
                    "followers": artist.get("followers", {}).get("total", 0),
                    "image": artist["images"][0]["url"] if artist["images"] else None
                })
            
            return artists
        except Exception as e:
            logger.error(f"Error searching artists with query '{query}': {e}")
            return []
    
    def find_related_artists(self, artist_url: str) -> List[str]:
        """
        Finds all artists that have a feature with the given artist.
        
        Preserves the exact functionality from the original implementation.
        
        Args:
            artist_url (str): Spotify URL of the artist.
        
        Returns:
            list: Related artist URLs.
        """
        try:
            artist_id = artist_url.split("/")[-1]
            featured_urls = set()
            
            # Get all albums and singles for the artist
            albums = self.safe_request(
                self.sp.artist_albums, 
                artist_id, 
                album_type="album,single", 
                country="US"
            )
            
            for album in albums["items"]:
                # Get tracks for each album
                tracks = self.safe_request(self.sp.album_tracks, album["id"])
                for track in tracks["items"]:
                    # Find featured artists (excluding the main artist)
                    for artist in track["artists"]:
                        if artist["id"] != artist_id:
                            featured_urls.add(artist["external_urls"]["spotify"])
            
            logger.info(f"Found {len(featured_urls)} related artists for {artist_url}")
            return list(featured_urls)
            
        except Exception as e:
            logger.error(f"Error finding related artists for '{artist_url}': {e}")
            return []

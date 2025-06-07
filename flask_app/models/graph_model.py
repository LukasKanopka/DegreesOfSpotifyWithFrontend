from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Artist:
    """
    Data model for an artist.
    """
    name: str
    url: str
    spotify_id: str
    popularity: int = 0
    genres: List[str] = None
    followers: int = 0
    image_url: Optional[str] = None
    
    def __post_init__(self):
        if self.genres is None:
            self.genres = []
    
    @classmethod
    def from_spotify_data(cls, spotify_data: Dict[str, Any]) -> 'Artist':
        """
        Create an Artist instance from Spotify API data.
        
        Args:
            spotify_data: Raw data from Spotify API.
        
        Returns:
            Artist instance.
        """
        return cls(
            name=spotify_data.get("name", ""),
            url=spotify_data.get("external_urls", {}).get("spotify", ""),
            spotify_id=spotify_data.get("id", ""),
            popularity=spotify_data.get("popularity", 0),
            genres=spotify_data.get("genres", []),
            followers=spotify_data.get("followers", {}).get("total", 0),
            image_url=spotify_data["images"][0]["url"] if spotify_data.get("images") else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert artist to dictionary representation.
        
        Returns:
            Dictionary representation of the artist.
        """
        return {
            "name": self.name,
            "url": self.url,
            "spotify_id": self.spotify_id,
            "popularity": self.popularity,
            "genres": self.genres,
            "followers": self.followers,
            "image_url": self.image_url
        }

@dataclass
class Connection:
    """
    Data model for a connection between two artists.
    """
    from_artist_url: str
    to_artist_url: str
    connection_type: str = "collaboration"  # collaboration, feature, etc.
    strength: float = 1.0  # Connection strength (could be based on number of collaborations)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert connection to dictionary representation.
        
        Returns:
            Dictionary representation of the connection.
        """
        return {
            "from_artist_url": self.from_artist_url,
            "to_artist_url": self.to_artist_url,
            "connection_type": self.connection_type,
            "strength": self.strength
        }

@dataclass
class SearchResult:
    """
    Data model for search results.
    """
    found: bool
    start_artist: str
    end_artist: str
    algorithm: str
    degrees: Optional[int] = None
    artists_searched: Optional[int] = None
    path_urls: List[str] = None
    path_names: List[str] = None
    search_time: Optional[float] = None
    timestamp: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.path_urls is None:
            self.path_urls = []
        if self.path_names is None:
            self.path_names = []
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search result to dictionary representation.
        
        Returns:
            Dictionary representation of the search result.
        """
        return {
            "found": self.found,
            "start_artist": self.start_artist,
            "end_artist": self.end_artist,
            "algorithm": self.algorithm,
            "degrees": self.degrees,
            "artists_searched": self.artists_searched,
            "path_urls": self.path_urls,
            "path_names": self.path_names,
            "search_time": self.search_time,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "error_message": self.error_message
        }

@dataclass
class GraphStats:
    """
    Data model for graph statistics.
    """
    total_artists: int
    total_connections: int
    average_connections: float
    most_connected_artist: Optional[str] = None
    most_connections_count: Optional[int] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert graph stats to dictionary representation.
        
        Returns:
            Dictionary representation of the graph stats.
        """
        return {
            "total_artists": self.total_artists,
            "total_connections": self.total_connections,
            "average_connections": self.average_connections,
            "most_connected_artist": self.most_connected_artist,
            "most_connections_count": self.most_connections_count,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

@dataclass
class SearchProgress:
    """
    Data model for tracking search progress.
    """
    search_id: str
    status: str  # starting, running, completed, failed
    progress: int  # 0-100
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[SearchResult] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert search progress to dictionary representation.
        
        Returns:
            Dictionary representation of the search progress.
        """
        return {
            "search_id": self.search_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result.to_dict() if self.result else None,
            "error": self.error
        }
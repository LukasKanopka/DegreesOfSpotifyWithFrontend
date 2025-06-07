import csv
import os
import logging
from typing import Dict, List, Optional, Tuple, Callable

from config import Config

logger = logging.getLogger(__name__)

class GraphService:
    """
    Service for managing the artist graph and performing search algorithms.
    
    Preserves all existing functionality from the original Spotipy.py implementation
    including BFS, DFS algorithms and CSV-based adjacency list management.
    """
    
    def __init__(self):
        """Initialize graph service."""
        self.csv_file = Config.CSV_FILE
        logger.info(f"Graph service initialized with CSV file: {self.csv_file}")
    
    def read_adjacency_list(self) -> Dict[str, List[str]]:
        """
        Reads the adjacency list from the CSV file.
        
        Preserves the exact functionality from the original implementation.
        
        Returns:
            dict: Adjacency list mapping artist URLs to related artist URLs.
        """
        if not os.path.exists(self.csv_file):
            logger.warning(f"CSV file {self.csv_file} does not exist, returning empty adjacency list")
            return {}
        
        adjacency_list = {}
        try:
            with open(self.csv_file, mode="r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:  # Skip empty rows
                        artist_url = row[0]
                        related_urls = row[1:]
                        adjacency_list[artist_url] = related_urls
            
            logger.info(f"Loaded adjacency list with {len(adjacency_list)} artists")
            return adjacency_list
            
        except Exception as e:
            logger.error(f"Error reading adjacency list from {self.csv_file}: {e}")
            return {}
    
    def write_adjacency_list(self, adjacency_list: Dict[str, List[str]]) -> bool:
        """
        Writes the adjacency list to the CSV file.
        
        Preserves the exact functionality from the original implementation.
        
        Args:
            adjacency_list (dict): Adjacency list mapping artist URLs to related artist URLs.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(self.csv_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                for artist_url, related_urls in adjacency_list.items():
                    writer.writerow([artist_url] + related_urls)
            
            logger.info(f"Successfully wrote adjacency list with {len(adjacency_list)} artists")
            return True
            
        except Exception as e:
            logger.error(f"Error writing adjacency list to {self.csv_file}: {e}")
            return False
    
    def add_artist_connections(self, artist_url: str, related_urls: List[str]) -> bool:
        """
        Add connections for an artist to the adjacency list.
        
        Args:
            artist_url (str): URL of the artist.
            related_urls (list): List of related artist URLs.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            adjacency_list = self.read_adjacency_list()
            adjacency_list[artist_url] = related_urls
            return self.write_adjacency_list(adjacency_list)
        except Exception as e:
            logger.error(f"Error adding artist connections: {e}")
            return False
    
    def get_artist_connections(self, artist_url: str) -> List[str]:
        """
        Get connections for an artist from the adjacency list.
        
        Args:
            artist_url (str): URL of the artist.
            
        Returns:
            list: List of related artist URLs.
        """
        adjacency_list = self.read_adjacency_list()
        return adjacency_list.get(artist_url, [])
    
    def find_related_artists_in_memory(self, adjacency_list: Dict[str, List[str]], artist_url: str) -> List[str]:
        """
        Operates on the adjacency list in memory instead of in the CSV for faster access times.
        
        Preserves the exact functionality from the original implementation.
        
        Args:
            adjacency_list (dict): The adjacency list in memory.
            artist_url (str): The Spotify URL of the artist.
        
        Returns:
            list: Related artist URLs.
        """
        if artist_url in adjacency_list:
            return adjacency_list[artist_url]
        
        # If not found in memory, return empty list
        logger.debug(f"Artist {artist_url} not found in memory.")
        return []
    
    def breadth_first_search(self, starting_url: str, ending_url: str, 
                           progress_callback: Optional[Callable[[int, str], None]] = None) -> Optional[List]:
        """
        Finds the shortest path between two artists using BFS.
        
        Preserves the exact functionality from the original implementation.
        
        Args:
            starting_url (str): URL of the starting artist.
            ending_url (str): URL of the ending artist.
            progress_callback: Optional callback for progress updates.
        
        Returns:
            list: A list containing:
                - The degree of separation between the artists.
                - The number of artists searched.
                - The shortest path as a list of URLs.
            Returns None if no path is found.
        """
        try:
            adjacency_list = self.read_adjacency_list()  # Load adjacency list once
            url_counter = 0
            queue = [(starting_url, [starting_url])]
            visited = set()
            
            if progress_callback:
                progress_callback(10, "Starting BFS search...")
            
            while queue:
                current_url, path = queue.pop(0)
                url_counter += 1
                
                # Update progress periodically
                if progress_callback and url_counter % 10 == 0:
                    progress_callback(
                        min(90, 10 + (url_counter * 80 // 1000)), 
                        f"Searched {url_counter} artists..."
                    )
                
                # If we find the target artist, return the result
                if current_url == ending_url:
                    if progress_callback:
                        progress_callback(100, "Connection found!")
                    return [len(path) - 1, url_counter] + path
                
                if current_url not in visited:
                    visited.add(current_url)
                    neighbors = self.find_related_artists_in_memory(adjacency_list, current_url)
                    
                    # Check if the ending URL is directly among neighbors
                    if ending_url in neighbors:
                        if progress_callback:
                            progress_callback(100, "Connection found!")
                        return [len(path), url_counter] + path + [ending_url]
                    
                    # Add unvisited neighbors to the queue
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            queue.append((neighbor, path + [neighbor]))
            
            # If no path is found, return None
            if progress_callback:
                progress_callback(100, "No connection found")
            return None
            
        except Exception as e:
            logger.error(f"Error in BFS search: {e}")
            if progress_callback:
                progress_callback(100, f"Search failed: {str(e)}")
            return None
    
    def depth_first_search(self, starting_url: str, ending_url: str,
                          progress_callback: Optional[Callable[[int, str], None]] = None) -> Optional[List]:
        """
        Uses DFS to find any path between two artists.
        
        Preserves the exact functionality from the original implementation.
        Switched from recursive to iterative to avoid recursion limit in large graphs.
        
        Args:
            starting_url (str): Spotify URL of the starting artist.
            ending_url (str): Spotify URL of the ending artist.
            progress_callback: Optional callback for progress updates.
        
        Returns:
            list: Path of artist URLs from start to end, or None if no connection.
        """
        try:
            url_counter = 0
            adjacency_list = self.read_adjacency_list()
            
            # Initialize stack for iterative DFS
            stack = [(starting_url, [starting_url])]  # Each element is (current_url, path)
            visited = set()
            
            if progress_callback:
                progress_callback(10, "Starting DFS search...")
            
            while stack:
                current_url, path = stack.pop()
                url_counter += 1
                
                # Update progress periodically
                if progress_callback and url_counter % 10 == 0:
                    progress_callback(
                        min(90, 10 + (url_counter * 80 // 1000)), 
                        f"Searched {url_counter} artists..."
                    )
                
                # If the current node is the target, return the path
                if current_url == ending_url:
                    if progress_callback:
                        progress_callback(100, "Connection found!")
                    return [len(path) - 1] + [str(url_counter)] + path
                
                # Mark as visited
                if current_url not in visited:
                    visited.add(current_url)
                    
                    # Get neighbors (related artists)
                    neighbors = self.find_related_artists_in_memory(adjacency_list, current_url)
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            # Append neighbor and the updated path to the stack
                            stack.append((neighbor, path + [neighbor]))
            
            # If the loop completes without finding the ending URL, return None
            if progress_callback:
                progress_callback(100, "No connection found")
            logger.info("No connection found between the artists in our database.")
            return None
            
        except Exception as e:
            logger.error(f"Error in DFS search: {e}")
            if progress_callback:
                progress_callback(100, f"Search failed: {str(e)}")
            return None
    
    def get_graph_stats(self) -> Dict[str, int]:
        """
        Get statistics about the current graph.
        
        Returns:
            dict: Statistics including number of artists, connections, etc.
        """
        try:
            adjacency_list = self.read_adjacency_list()
            total_artists = len(adjacency_list)
            total_connections = sum(len(connections) for connections in adjacency_list.values())
            
            return {
                "total_artists": total_artists,
                "total_connections": total_connections,
                "average_connections": total_connections / total_artists if total_artists > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting graph stats: {e}")
            return {"total_artists": 0, "total_connections": 0, "average_connections": 0}
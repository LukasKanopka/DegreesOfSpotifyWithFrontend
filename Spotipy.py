import time
import datetime
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import os
from dotenv import load_dotenv

load_dotenv()

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(
    client_id = os.getenv("CLIENT_ID"),
    client_secret = os.getenv("CLIENT_SECRET")
)
sp = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager,
    requests_timeout=10  # 10-second timeout for all requests
)

CSV_FILE = "adjacency_list.csv"


def safe_request(func, *args, **kwargs):
    """
    Executes a Spotify API request with retry logic, handling rate limits.

    Tracks request timing and logs when requests are delayed due to hitting the rate limit.
    Args:
        func: The Spotipy function to call.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the Spotipy API call.

    Raises:
        Exception: If all retries fail or rate-limiting persists.
    """
    max_retries = 3
    delay = 10  # Fixed delay in seconds between retries

    for attempt in range(max_retries):
        try:
            # Log the request time
            print(f"Sending request...", flush=True)
            time.sleep(0.333)  # Rate limit: 3 requests per second

            # Execute the function
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in request: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...", flush=True)
                time.sleep(delay)
            else:
                print("Maximum retries reached. Request failed.")
                raise


def read_adjacency_list():
    """
    Reads the adjacency list from the CSV file.

    Returns:
        dict: Adjacency list mapping artist URLs to related artist URLs.
    """
    if not os.path.exists(CSV_FILE):
        return {}

    adjacency_list = {}
    with open(CSV_FILE, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            artist_url = row[0]
            related_urls = row[1:]
            adjacency_list[artist_url] = related_urls
    return adjacency_list

def write_adjacency_list(adjacency_list):
    """
    Writes the adjacency list to the CSV file.

    Args:
        adjacency_list (dict): Adjacency list mapping artist URLs to related artist URLs.
    """
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        for artist_url, related_urls in adjacency_list.items():
            writer.writerow([artist_url] + related_urls)

def get_artist_url(artist_name):
    """
    Gets the Spotify URL for an artist by name.

    Args:
        artist_name (str): The name of the artist.

    Returns:
        str: Spotify URL for the artist or None if not found.
    """
    result = safe_request(sp.search, q=artist_name, type="artist", limit=1)
    if not result["artists"]["items"]:
        print("No artist with this name exists...")
        return None
    return result["artists"]["items"][0]["external_urls"]["spotify"]

def get_artist_name(artist_url):
    """
    Retrieves the artist's name from their Spotify URL.

    Args:
        artist_url (str): Spotify URL of the artist.

    Returns:
        str: Name of the artist, or None if the artist is not found.
    """
    try:
        artist_id = artist_url.split("/")[-1]
        result = safe_request(sp.artist, artist_id)
        return result["name"] if result else None
    except Exception as e:
        print(f"Error fetching artist name: {e}")
        return None



def make_bidirectional_connections(adjacency_list, artist_url, related_urls):
    """
    Ensures that all connections in the adjacency list are bidirectional.

    Args:
        adjacency_list (dict): Current adjacency list.
        artist_url (str): URL of the artist whose connections are being updated.
        related_urls (list): List of related artist URLs to be added bidirectionally.

    Returns:
        dict: Updated adjacency list with bidirectional connections.
    """
    for related_url in related_urls:
        if related_url not in adjacency_list:
            adjacency_list[related_url] = []
        if artist_url not in adjacency_list[related_url]:
            print(f"Adding reverse connection: {related_url} -> {artist_url}", flush=True)
            adjacency_list[related_url].append(artist_url)
    return adjacency_list

def find_related_artists(artist_url):
    """
    Finds all artists that have a feature with the given artist.
    Ensures bidirectional connections are maintained.

    Args:
        artist_url (str): Spotify URL of the artist.

    Returns:
        list: Related artist URLs.
    """
    adjacency_list = read_adjacency_list()

    if artist_url in adjacency_list:
        return adjacency_list[artist_url]

    artist_id = artist_url.split("/")[-1]
    featured_urls = set()

    albums = safe_request(sp.artist_albums, artist_id, album_type="album,single", country="US")
    for album in albums["items"]:
        tracks = safe_request(sp.album_tracks, album["id"])
        for track in tracks["items"]:
            for artist in track["artists"]:
                if artist["id"] != artist_id:
                    featured_urls.add(artist["external_urls"]["spotify"])

    adjacency_list[artist_url] = list(featured_urls)

    # Make connections bidirectional
    adjacency_list = make_bidirectional_connections(adjacency_list, artist_url, list(featured_urls))

    write_adjacency_list(adjacency_list)

    return list(featured_urls)

def breadth_first(starting_url, ending_url):
    """
    Uses BFS to find the shortest path between two artists.

    Args:
        starting_url (str): Spotify URL of the starting artist.
        ending_url (str): Spotify URL of the ending artist.

    Returns:
        list: Path of artist URLs from start to end, or None if no connection.
    """
    url_counter = 0
    queue = [(starting_url, [starting_url])]
    visited = set()


    while queue:
        current_url, path = queue.pop(0)

        url_counter += 1

        print(current_url)

        if current_url == ending_url:
            return [len(path) - 1] + path

        if current_url not in visited:
            visited.add(current_url)
            neighbors = find_related_artists(current_url)

            # Check if ending_url is in neighbors
            if ending_url in neighbors:
                return [len(path)] + [str(url_counter)] + path + [ending_url]

            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

    return None

def depth_first(starting_url, ending_url):
    """
    Uses DFS to find any path between two artists

    Args:
        starting_url (str): Spotify URL of the starting artist.
        ending_url (str): Spotify URL of the ending artist.

    Returns:
        list: Path of artist URLs from start to end, or None if no connection.
    """
    def dfs_recursive(current_url, visited, path):
        """
        Inner recursive function for DFS

        Args:
            current_url (str): Spotify URL of the current artist being visited.
            visited (set): Set of visited artists URLs.
            path (list): Path of artist URLs currently being explored.

        Returns:
            list: Path of artist URLs from start to end, or None if no connection.
        """
        visited.add(current_url)
        path.append(current_url)

        # if current audience is target audience, return path
        if current_url == ending_url:
            return [len(path) - 1] + path
        # get related artists
        neighbors = find_related_artists(current_url)
        for neighbor in neighbors:
            if neighbor not in visited:
                result = dfs_recursive(neighbor, visited, path + [neighbor])
                if result:
                    return result
        # if no path found from current artist
        path.pop()
        return None
    # initialize visited set and path list
    visited = set()
    path = []
    return dfs_recursive(starting_url, visited, path)

def main():
    """
    Main function to run the BFS and DFS program.
    """
    artist_name_1 = input("Enter the first artist name: ").strip()
    artist_name_2 = input("Enter the second artist name: ").strip()

    start_url = get_artist_url(artist_name_1)
    end_url = get_artist_url(artist_name_2)

    if not start_url or not end_url:
        print("Could not find one or both artists. Exiting.")
        return

    print("\nChoose a search method:")
    print("1. Breadth-First Search (BFS)")
    print("2. Depth-First Search (DFS)")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        print(f"\nFinding shortest path between {artist_name_1} and {artist_name_2} using BFS...")
        result = breadth_first(start_url, end_url)
    if choice == "2":
        print(f"\nFinding a path between {artist_name_1} and {artist_name_2} using DFS...")
        result = depth_first(start_url, end_url)
    else:
        print("Not a valid choice. Exiting")
        return

    if result:
        degrees = result[0]
        path = result[1:]
        #Converts URLs to artist names for better readability
        path_names = [get_artist_url(url) for url in path]
        print(f"\nDegrees of separation: {degrees}")
        print(" -> ".join(path_names))
    else:
        print("No connection found between the artists.")

if __name__ == "__main__":
    main()

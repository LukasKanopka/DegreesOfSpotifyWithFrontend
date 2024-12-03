import time
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import os

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(
    client_id="84f6ff8152574772a628041b3452a46a",
    client_secret="5c2fc99df4274710b19f3805323922dc",
)
sp = spotipy.Spotify(
    client_credentials_manager=client_credentials_manager,
    requests_timeout=10  # 10-second timeout for all requests
)

CSV_FILE = "adjacency_list.csv"

def safe_request(func, *args, retries=3, delay=5, **kwargs):
    """
    Executes a Spotify API request with retry logic.

    Args:
        func: The Spotipy function to call.
        *args: Positional arguments for the function.
        retries (int): Number of retry attempts.
        delay (int): Delay in seconds between retries.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the Spotipy API call.

    Raises:
        requests.exceptions.ReadTimeout: If all retries fail.
    """
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ReadTimeout:
            if attempt < retries - 1:
                print(f"Timeout occurred. Retrying {attempt + 1}/{retries}...")
                time.sleep(delay)
            else:
                print("Failed after retries. Exiting...")
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

def find_related_artists(artist_url):
    """
    Finds all artists that have a feature with the given artist.
    Checks the CSV first before querying the Spotify API.

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
    queue = [(starting_url, [starting_url])]
    visited = set()


    while queue:
        current_url, path = queue.pop(0)

        print(current_url)

        if current_url == ending_url:
            return [len(path) - 1] + path

        if current_url not in visited:
            visited.add(current_url)
            neighbors = find_related_artists(current_url)

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

        # if current audience is target audience, return path.
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
        result = breadth_first(start_url, end_url)
    else:
        print("Not a valid choice. Exiting")
        return

    if result:
        degrees = result[0]
        path = result[1:]
        print(f"\nDegrees of separation: {degrees}")
        print(" -> ".join(path))
    else:
        print("No connection found between the artists.")

if __name__ == "__main__":
    main()

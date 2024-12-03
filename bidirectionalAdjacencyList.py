"""
Noticed that the adjacency list is not bidirectional in all cases
There are some songs with features that only show up on one artist's discography instead of both

To fix this, this program iterates through the csv and checks for one directional connections and makes them bidirectional

Shouldn't be needed anymore as this logic is now implemented into Spotipy.py but this was used to clean up the initial data
instead of having to create a new adjacency list and pull all the data again.
"""
import csv

CSV_FILE = "adjacency_list.csv"

def read_adjacency_list():
    """
    Reads the adjacency list from the CSV file.

    Returns:
        dict: Adjacency list mapping artist URLs to related artist URLs.
    """
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

def make_connections_bidirectional(adjacency_list):
    """
    Ensures all connections in the adjacency list are bidirectional.

    Args:
        adjacency_list (dict): Adjacency list mapping artist URLs to related artist URLs.

    Returns:
        dict: Updated adjacency list with bidirectional connections.
    """
    updated_adjacency_list = {k: set(v) for k, v in adjacency_list.items()}  # Convert lists to sets for easier manipulation

    for artist_url, related_urls in adjacency_list.items():
        for related_url in related_urls:
            if related_url not in updated_adjacency_list:
                updated_adjacency_list[related_url] = set()  # Ensure related artist exists in the adjacency list
            if artist_url not in updated_adjacency_list[related_url]:
                updated_adjacency_list[related_url].add(artist_url)  # Add the reverse connection
                print(f"Adding reverse connection: {related_url} -> {artist_url}")

    # Convert sets back to lists for saving to CSV
    return {k: list(v) for k, v in updated_adjacency_list.items()}

def main():
    """
    Main function to fix one-way connections in the adjacency list.
    """
    print("Reading current adjacency list...")
    adjacency_list = read_adjacency_list()

    print("Making connections bidirectional...")
    updated_adjacency_list = make_connections_bidirectional(adjacency_list)

    print("Writing updated adjacency list to CSV...")
    write_adjacency_list(updated_adjacency_list)

    print("All connections are now bidirectional.")

if __name__ == "__main__":
    main()

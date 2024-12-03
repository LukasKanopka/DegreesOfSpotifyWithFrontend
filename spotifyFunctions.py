'''
Testing File For API Key

Gets API Key From Client, Copies Key to Clipboard, and Prints Out Top 10 Drake Songs
To Ensure That the API Access is Working

Also now updates the .cache with the new API key!

Prints Out Any Errors Such as 429: Rate Limit Exceeded

Toutorial For Spotify Authorization: https://www.youtube.com/watch?v=WAmEZBEeNmg
'''

import spotipy
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import clipboard

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
cache_file = ".cache"


print("Client ID:" , client_id, "Client Secret:", client_secret)

def update_access_token(cache_file, new_token):
    """
    Replaces the current access token in the .cache file with a new token.

    Args:
        cache_file (str): Path to the .cache file.
        new_token (str): The new access token to replace the old one.
    """
    try:
        # Read the existing data from the cache file
        with open(cache_file, "r") as file:
            data = json.load(file)

        # Update the access token
        data["access_token"] = new_token

        # Write the updated data back to the cache file
        with open(cache_file, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Access token updated successfully in {cache_file}")

    except:
        print("Error in updating cache token...")



def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None

    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)

    print("Response Status Code:", result.status_code)
    print("Response Headers:", result.headers)
    print("Response Content:", result.content)
    print("Response Text:", result.text)
    print("Request URL:", result.url)
    print("Request Headers:", result.request.headers)
    print("Request Body:", result.request.body)

    json_result = json.loads(result.content)["tracks"]
    return json_result



token = get_token()
print("Token: ", token)
clipboard.copy(token)
print("Token was copied to clipboard! Make sure to update the token in cache")
update_access_token(cache_file, token)
print(" ")


result = search_for_artist(token, "Drake ")
artist_id = result["id"]

songs = get_songs_by_artist(token, artist_id)

print(" ")
print("Top Ten Songs for:", result["name"])
print(" ")

for idx, song in enumerate(songs):
    print(f"{idx + 1}. {song['name']}")
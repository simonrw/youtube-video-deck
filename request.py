#!/usr/bin/env python


import requests
import pprint
from joblib import Memory
import os
import dotenv

username = "outsidexbox"


memory = Memory(location="/tmp")

@memory.cache
def fetch_channel_info(key, username):
    # Get the uploads url
    url = "https://www.googleapis.com/youtube/v3/channels?part={part}&key={key}&forUsername={username}".format(
            part="contentDetails", key=key, username=username)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

@memory.cache
def fetch_items(key, uploads_id):
    url = "https://www.googleapis.com/youtube/v3/playlistItems?key={key}&part=contentDetails&maxResults=50&playlistId={playlist_id}".format(
        key=key, playlist_id=uploads_id)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    dotenv.load_dotenv()

    key = os.environ["GOOGLE_API_KEY"]

    result = fetch_channel_info(key, username)
    uploads_id = result["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    pprint.pprint(fetch_items(key, uploads_id))

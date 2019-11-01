#!/usr/bin/env python


import requests
import pprint
from joblib import Memory
import os
import dotenv

username = "outsidexbox"


memory = Memory("/tmp")


class Client:
    def __init__(self, key):
        self.key = key

    def _fetch_channel_info(self, username):
        url = "https://www.googleapis.com/youtube/v3/channels?part={part}&key={key}&forUsername={username}".format(
            part="contentDetails", key=self.key, username=username
        )
        r = requests.get(url)
        r.raise_for_status()
        results = r.json()
        return results["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _fetch_items(self, uploads_id):
        url = "https://www.googleapis.com/youtube/v3/playlistItems?key={key}&part=contentDetails&maxResults=50&playlistId={playlist_id}".format(
            key=self.key, playlist_id=uploads_id
        )
        r = requests.get(url)
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    dotenv.load_dotenv()

    key = os.environ["GOOGLE_API_KEY"]

    client = Client(key)

    uploads_id = client._fetch_channel_info(username)
    pprint.pprint(client._fetch_items(uploads_id))

import requests
from dataclasses import dataclass
from typing import Optional
import enum


class ItemType(enum.Enum):
    CHANNEL = "channel"
    PLAYLIST = "playlist"

    @classmethod
    def from_(cls, value):
        if value == "ItemType.CHANNEL":
            return cls.CHANNEL
        elif value == "ItemType.PLAYLIST":
            return cls.PLAYLIST
        else:
            raise ValueError(f"Invalid item type: {value}")


@dataclass
class Thumbnail:
    url: str
    width: Optional[int]
    height: Optional[int]


@dataclass
class SearchItem:
    id: str
    title: str
    description: str
    thumbnail: Thumbnail
    channel_title: str
    item_type: ItemType


class YoutubeClient(object):
    """
    Provides an abstraction over the Youtube API.

    This object decouples the domain models from the Youtube API. It supports
    the following methods:

    * Search Youtube for either the channel or playlist with the given name
    * Fetch new items (videos) since a specified time
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        # TODO: add any request parameters

    def _fetch(self, url, *, params=None):
        """
        Helper method for fetching data from the Youtube API. This:

        * provides a mocking point for testing the rest of the API, and
        * unifies request making
        """
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def search(self, term):
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": term,
            "type": "channel,playlist",
            "maxResults": 25,
        }

        data = self._fetch(url, params=params)

        for item in data["items"]:
            title = item["snippet"]["title"]
            description = item["snippet"]["description"]
            channel_title = item["snippet"]["channelTitle"]
            thumbnail = Thumbnail(
                url=item["snippet"]["thumbnails"]["high"]["url"],
                width=item["snippet"]["thumbnails"]["high"].get("width"),
                height=item["snippet"]["thumbnails"]["high"].get("height"),
            )

            if item["id"]["kind"] == "youtube#channel":
                yield SearchItem(
                    id=item["id"]["channelId"],
                    item_type=ItemType.CHANNEL,
                    title=title,
                    description=description,
                    channel_title=channel_title,
                    thumbnail=thumbnail,
                )
            elif item["id"]["kind"] == "youtube#playlist":
                yield SearchItem(
                    id=item["id"]["playlistId"],
                    item_type=ItemType.PLAYLIST,
                    title=title,
                    description=description,
                    channel_title=channel_title,
                    thumbnail=thumbnail,
                )
            else:
                raise ValueError(f"Invalid item kind: {item['id']['kind']}")

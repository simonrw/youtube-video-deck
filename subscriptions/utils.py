import requests
from dataclasses import dataclass
from typing import Optional
import enum
import logging
from .models import Subscription, Video
from django.utils import timezone
from django.db.utils import IntegrityError
from django.utils.dateparse import parse_datetime


LOGGER = logging.getLogger("ytvd.subscriptions.utils")


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

    def fetch_latest(self, *, channel_id, since):
        page_id = None
        url = "https://www.googleapis.com/youtube/v3/search"
        while True:
            params = {
                "key": self.api_key,
                "part": "snippet",
                "maxResults": 25,
                "channelId": channel_id,
                "publishedAfter": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            if page_id is not None:
                params["pageToken"] = (page_id,)

            data = self._fetch(url, params=params)

            for item in data["items"]:
                if item["id"]["kind"] != "youtube#video":
                    LOGGER.warning(
                        "Unexpected item found in list: %s, expected youtube#video",
                        item["id"]["kind"],
                    )
                    continue

                published_at = parse_datetime(item["snippet"]["publishedAt"])

                yield Video(
                    youtube_id=item["id"]["videoId"],
                    name=item["snippet"]["title"],
                    description=item["snippet"]["description"],
                    published_at=published_at,
                    thumbnail_url=item["snippet"]["thumbnails"]["high"]["url"],
                )

            # Break condition, no more pages
            if "nextPageToken" in data:
                page_id = data["nextPageToken"]
            else:
                break

        return []


class Crawler:
    """
    Given a subscription id and type, crawl the videos for that
    subscription to find any new ones.
    """

    def __init__(self, client):
        self.client = client

    def crawl(self, *, user):
        """
        Go through all of the subscriptions, check for latest videos
        and update
        """
        subscriptions = Subscription.objects.filter(user__username=user.username).all()
        for sub in subscriptions:
            self.crawl_subscription(sub)

    def crawl_subscription(self, sub):
        LOGGER.info("Crawling for subscription %s", sub)
        now = timezone.now()
        if sub.last_checked is None:
            since = now - timezone.timedelta(days=90)
        else:
            since = sub.last_checked

        videos = self.client.fetch_latest(channel_id=sub.youtube_id, since=since)

        for video in videos:
            video.subscription = sub
            try:
                video.save()
            except IntegrityError as e:
                # Video already exists, so do not bother updating, and silently
                # skip this
                continue

        # Finally update the last_checked field
        sub.last_checked = now
        sub.save()

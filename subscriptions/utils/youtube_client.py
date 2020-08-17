import requests
import re
import logging
from ..models import Video
from .types import ItemType, Thumbnail, SearchItem
from django.utils.dateparse import parse_datetime
from datetime import time


LOGGER = logging.getLogger("ytvd.subscriptions.utils.youtube_client")


class YoutubeClient(object):
    """
    Provides an abstraction over the Youtube API.

    This object decouples the domain models from the Youtube API. It supports
    the following methods:

    * Search Youtube for either the channel or playlist with the given name
    * Fetch new items (videos) since a specified time
    """

    duration_re = re.compile(
        r"""
        PT  # Always starts with PT as we are parsing a time duration
        ((?P<hours>\d+)H)?
        ((?P<minutes>\d+)M)?
        ((?P<seconds>\d+)S)?
        """,
        re.VERBOSE,
    )

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
            "maxResults": 50,
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

    def fetch_latest_from_channel(self, *, channel_id, since):
        page_id = None
        url = "https://www.googleapis.com/youtube/v3/search"
        while True:
            params = {
                "key": self.api_key,
                "part": "snippet",
                "maxResults": 50,
                "channelId": channel_id,
                "type": "video",
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

                if published_at <= since:
                    # Should never happen as we are querying the API since the
                    # `since` parameter. We want to log this case in case our
                    # assumptions are incorrect.
                    LOGGER.warning(
                        "API returned an item later than the `since` value, despite giving a `publishedAt` value. This is unexpected."
                    )
                    continue

                video_id = item["id"]["videoId"]
                details = self.fetch_video_details(video_id)
                duration = self._parse_duration(details[video_id]["duration"])

                yield Video(
                    youtube_id=video_id,
                    name=item["snippet"]["title"],
                    description=item["snippet"]["description"],
                    published_at=published_at,
                    thumbnail_url=item["snippet"]["thumbnails"]["high"]["url"],
                    duration=duration,
                )

            # Break condition, no more pages
            if "nextPageToken" in data:
                page_id = data["nextPageToken"]
            else:
                break

    def fetch_latest_from_playlist(self, *, playlist_id, since):
        page_id = None
        url = "https://www.googleapis.com/youtube/v3/playlistItems"
        while True:
            params = {
                "key": self.api_key,
                "part": "snippet",
                "maxResults": 50,
                "playlistId": playlist_id,
            }

            if page_id is not None:
                params["pageToken"] = (page_id,)

            data = self._fetch(url, params=params)

            for item in data["items"]:
                resource = item["snippet"]["resourceId"]
                if resource["kind"] != "youtube#video":
                    LOGGER.warning(
                        "Unexpected item found in list: %s, expected youtube#playlistItem",
                        resource["kind"],
                    )
                    continue

                published_at = parse_datetime(item["snippet"]["publishedAt"])

                if published_at <= since:
                    continue

                video_id = resource["videoId"]
                details = self.fetch_video_details(video_id)
                duration = self._parse_duration(details[video_id]["duration"])

                yield Video(
                    youtube_id=video_id,
                    name=item["snippet"]["title"],
                    description=item["snippet"]["description"],
                    published_at=published_at,
                    thumbnail_url=item["snippet"]["thumbnails"]["high"]["url"],
                    duration=duration,
                )

            # Break condition, no more pages
            if "nextPageToken" in data:
                page_id = data["nextPageToken"]
            else:
                break

    def fetch_video_details(self, *video_ids):
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "key": self.api_key,
            "id": ",".join(video_ids),
            "part": "contentDetails",
        }
        data = self._fetch(url, params=params)
        results = {}
        for item in data["items"]:
            results[item["id"]] = item["contentDetails"]
        return results

    @classmethod
    def _parse_duration(cls, duration: str) -> time:
        match = cls.duration_re.match(duration)
        if not match:
            raise ValueError(f"Cannot parse duration: {duration}")

        hours = int(match.group("hours") or 0)
        minutes = int(match.group("minutes") or 0)
        seconds = int(match.group("seconds") or 0)

        return time(hours, minutes, seconds)

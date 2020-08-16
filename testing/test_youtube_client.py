from unittest import mock
from django.utils import timezone
import pytest
from subscriptions.utils.youtube_client import YoutubeClient
from subscriptions.utils.types import ItemType
from subscriptions.utils.crawler import Crawler
from subscriptions.models import Subscription, Video
from ytvd.settings import BASE_DIR
import os


@pytest.fixture(scope="session")
def response():
    import json

    def _inner(name):
        filename = os.path.join(
            BASE_DIR, "testing", "fixtures", f"{name}_response.json"
        )
        with open(filename) as infile:
            return json.load(infile)

    return _inner


def test_client_creation(api_key, client):
    assert client.api_key == api_key


@pytest.mark.webtest
def test_fetching(client):
    url = "https://httpbin.org/get"
    params = {"a": 10}
    json = client._fetch(url, params=params)
    assert json["args"]["a"] == "10"


@pytest.mark.webtest
def test_fetch_error(client):
    from requests.exceptions import HTTPError

    url = "https://httpbin.org/status/404"
    with pytest.raises(HTTPError) as exc_info:
        client._fetch(url)

    assert exc_info.match(r"404 Client Error")


def test_search_for_term(client, response):
    stub_response = response("search")
    with mock.patch.object(client, "_fetch") as fetch:
        fetch.return_value = stub_response

        results = list(client.search("outsidexbox"))

    # Check that fetch was called correctly
    fetch.assert_called_once_with(
        "https://www.googleapis.com/youtube/v3/search",
        params={
            "key": client.api_key,
            "part": "snippet",
            "q": "outsidexbox",
            "type": "channel,playlist",
            "maxResults": 50,
        },
    )

    # Check the first response, which should be the correct one (channel)
    assert results[0].id == "UCKk076mm-7JjLxJcFSXIPJA"
    assert results[0].item_type == ItemType.CHANNEL
    assert results[0].title == "outsidexbox"
    assert results[0].description.startswith("Daily videos from Outside Xbox")
    assert results[0].thumbnail.url.startswith("https://yt3.ggpht.com/-KVOLcjU8aUw")
    assert results[0].channel_title == "outsidexbox"

    # Check a response that is a playlist
    assert results[2].id == "PL_WcVABbXAhBz6NPfgBrutBXOhSj_SVgw"
    assert results[2].item_type == ItemType.PLAYLIST
    assert results[2].title.startswith("Horror Games!")
    assert results[2].description.startswith("Classic Outside Xbox horror")
    assert (
        results[2].thumbnail.url == "https://i.ytimg.com/vi/a6GennlwSR8/hqdefault.jpg"
    )
    assert results[2].channel_title == "outsidexbox"


def test_fetch_latest(client, response):
    stub_response_1 = response("fetch_latest_1")
    stub_response_2 = response("fetch_latest_2")
    stub_response_3 = response("fetch_latest_3")

    with mock.patch.object(client, "_fetch") as fetch:
        fetch.side_effect = [stub_response_1, stub_response_2, stub_response_3]

        videos = list(
            client.fetch_latest_from_channel(
                channel_id="UCKk076mm-7JjLxJcFSXIPJA",
                since=timezone.make_aware(timezone.datetime(2019, 9, 1)),
            )
        )
        assert len(videos) == 50

    # Check the first result
    assert videos[0].youtube_id == "7v-KIxHOhrs"
    assert videos[0].published_at == timezone.make_aware(
        timezone.datetime(2019, 9, 26, 17, 15, 22)
    )
    assert videos[0].name == "7 Transforming Bosses Who Made Us Regret Our Cockiness"
    assert videos[0].description.startswith(
        "Don't you just hate it when you encounter a videogame boss"
    )

    # TODO: check another video


def test_fetch_video_details(client, response, mocker):
    stub_response = response("video_details")
    id = "78XKGNmBmHw"
    mocker.patch.object(client, "_fetch", side_effect=[stub_response])

    meta = client.fetch_video_details(id)

    assert meta[id]["duration"] == "PT29M46S"


def test_fetch_from_playlist(client, response):
    stub_response_1 = response("playlist_1")
    stub_response_2 = response("playlist_2")

    with mock.patch.object(client, "_fetch") as fetch:
        fetch.side_effect = [stub_response_1, stub_response_2]

        videos = list(
            client.fetch_latest_from_playlist(
                playlist_id="PL7bmigfV0EqQzxcNpmcdTJ9eFRPBe-iZa",
                since=timezone.make_aware(timezone.datetime(2019, 10, 24)),
            )
        )
        assert len(videos) == 2

    assert videos[0].youtube_id == "XxVHNWoZO_c"
    assert videos[0].published_at == timezone.make_aware(
        timezone.datetime(2019, 11, 1, 21, 54, 51)
    )
    assert videos[0].name == "TGI Kubernetes 096: Grokking Kubernetes : kube-scheduler"
    assert videos[0].description.startswith(
        "Come hang out with Duffie Cooley as he does a bit of hands on hacking"
    )

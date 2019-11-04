from unittest import mock
import pytest
from subscriptions.utils import YoutubeClient, ItemType
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


@pytest.fixture
def api_key():
    return "API_KEY"


@pytest.fixture
def client(api_key):
    return YoutubeClient(api_key)


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

from unittest import mock
import pytest
from subscriptions.utils import YoutubeClient


@pytest.fixture
def api_key():
    return "API_KEY"

def test_client_creation(api_key):
    client = YoutubeClient(api_key)
    assert client.api_key == api_key

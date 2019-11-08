import pytest
from subscriptions.models import Subscription
from subscriptions.utils.youtube_client import YoutubeClient


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user("a", "a@example.com", "password")


@pytest.fixture
def subscription(user):
    return Subscription.objects.create(user=user, name="foo")


@pytest.fixture
def api_key():
    return "API_KEY"


@pytest.fixture
def client(api_key):
    return YoutubeClient(api_key)

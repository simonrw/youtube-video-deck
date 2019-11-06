import pytest
from subscriptions.models import Subscription


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user("a", "a@example.com", "password")


@pytest.fixture
def subscription(user):
    return Subscription.objects.create(user=user, name="foo")

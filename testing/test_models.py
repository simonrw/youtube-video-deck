import pytest
from subscriptions.models import Subscription


@pytest.mark.django_db
class TestSubscription:
    def test_create(self):
        Subscription.objects.create(name="foo")
        assert Subscription.objects.first().name == "foo"

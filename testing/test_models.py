import pytest
from django.utils import timezone

from subscriptions.models import Subscription, Video


pytestmark = pytest.mark.django_db


class TestSubscription:
    def test_create(self):
        Subscription.objects.create(name="foo")
        assert Subscription.objects.first().name == "foo"


class TestVideo:
    def test_create(self):
        ts = timezone.now()
        Video.objects.create(published_at=ts)
        assert Video.objects.first().published_at == ts
        assert Video.objects.first().watched == False

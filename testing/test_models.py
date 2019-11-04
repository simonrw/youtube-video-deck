import pytest
from django.utils import timezone

from subscriptions.models import Subscription, Video


pytestmark = pytest.mark.django_db


@pytest.fixture
def now():
    return timezone.now()


class TestSubscription:
    def test_create(self):
        Subscription.objects.create(name="foo")
        assert Subscription.objects.first().name == "foo"

    def test_has_videos(self, now):
        s = Subscription.objects.create(name="foo")
        s.video_set.create(published_at=now)

        assert Video.objects.first().published_at == now

    def test_unwatched_filter(self, now):
        s = Subscription.objects.create(name="foo")
        v1 = s.video_set.create(youtube_id="123", published_at=now)
        v2 = s.video_set.create(youtube_id="456", published_at=now, watched=True)

        unwatched = s.unwatched()
        assert list(unwatched) == [v1]



class TestVideo:
    def subscription(self):
        # Fixture
        return Subscription.objects.create(name="foo")

    def test_create(self, now):
        sub = self.subscription()

        Video.objects.create(published_at=now, subscription=sub)
        assert Video.objects.first().published_at == now
        assert Video.objects.first().watched == False

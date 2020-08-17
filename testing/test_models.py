from datetime import time
import pytest
from django.utils import timezone
from django.contrib.auth.models import User

from subscriptions.models import Subscription, Video


@pytest.fixture
def now():
    return timezone.now()


@pytest.mark.django_db
class TestSubscription:
    def test_create(self, user):
        Subscription.objects.create(user=user, name="foo")
        assert Subscription.objects.first().name == "foo"

    def test_has_videos(self, now, user):
        s = Subscription.objects.create(user=user, name="foo")
        s.videos.create(published_at=now)

        assert Video.objects.first().published_at == now

    def test_unwatched_filter(self, now, user):
        s = Subscription.objects.create(user=user, name="foo")
        v1 = s.videos.create(youtube_id="123", published_at=now)
        v2 = s.videos.create(youtube_id="456", published_at=now, watched=True)

        unwatched = s.unwatched()
        assert list(unwatched) == [v1]


class TestVideo:
    @pytest.mark.django_db
    def test_create(self, now, subscription):
        Video.objects.create(published_at=now, subscription=subscription)
        assert Video.objects.first().published_at == now
        assert Video.objects.first().watched == False

    def test_url_property(self, now):
        youtube_id = "foobar"
        video = Video(youtube_id=youtube_id)

        assert video.url == "https://www.youtube.com/watch?v={}".format(youtube_id)

    def test_duration(self, now):
        video = Video(youtube_id="foobar", duration=time(0, 29, 46))

        assert video.duration == time(0, 29, 46)


@pytest.mark.django_db
def test_subscriptions_belong_to_user():
    u1 = User.objects.create_user("a", "a@example.com", "password")
    sub1 = u1.subscriptions.create(name="foo", youtube_id="123")

    u2 = User.objects.create_user("b", "b@example.com", "password")
    sub2 = u2.subscriptions.create(name="bar", youtube_id="456")

    # Check that querying for u1's subscriptions does not return u2
    assert list(u1.subscriptions.all()) == [
        sub1,
    ]

from unittest import mock
import pytest
from django.utils import timezone
from subscriptions.models import Subscription, Video
from subscriptions.utils.crawler import Crawler


@pytest.mark.django_db
def test_crawler(client, user):
    last_checked = timezone.make_aware(timezone.datetime(2019, 9, 1))
    # Set up the database contents
    sub1 = Subscription.objects.create(
        user=user,
        name="outsidexbox",
        youtube_id="UCKk076mm-7JjLxJcFSXIPJA",
        type="ItemType.CHANNEL",
        last_checked=last_checked,
    )

    sub2 = Subscription.objects.create(
        user=user,
        name="outsidextra",
        youtube_id="ytid",
        type="ItemType.CHANNEL",
        last_checked=last_checked,
    )

    videos = [
        Video(
            youtube_id="123",
            subscription=sub1,
            published_at=timezone.make_aware(
                timezone.datetime(2019, 9, 26, 17, 15, 22)
            ),
        ),
        Video(
            youtube_id="456",
            subscription=sub2,
            published_at=timezone.make_aware(
                timezone.datetime(2019, 9, 26, 17, 15, 22)
            ),
        ),
    ]

    custom_now = timezone.now()
    with mock.patch.object(client, "fetch_latest") as fetch_latest:
        with mock.patch("subscriptions.utils.crawler.timezone.now") as mock_now:
            mock_now.return_value = custom_now
            fetch_latest.return_value = videos

            crawler = Crawler(client)
            crawler.crawl(user=user)

    assert [v.youtube_id for v in Video.objects.all()] == [v.youtube_id for v in videos]
    assert Subscription.objects.get(name="outsidexbox").last_checked == custom_now
    assert Subscription.objects.get(name="outsidextra").last_checked == custom_now


@pytest.mark.django_db
def test_crawler_with_existing_videos(client, user):
    last_checked = timezone.make_aware(timezone.datetime(2019, 9, 1))
    # Set up the database contents
    sub = Subscription.objects.create(
        user=user,
        name="outsidexbox",
        youtube_id="UCKk076mm-7JjLxJcFSXIPJA",
        type="ItemType.CHANNEL",
        last_checked=last_checked,
    )

    existing_video = Video(
        youtube_id="7v-KIxHOhrs",
        published_at=timezone.make_aware(timezone.datetime(2019, 9, 26, 17, 15, 22)),
    )
    existing_video.subscription = sub
    existing_video.watched = True
    existing_video.save()

    assert len(Video.objects.all()) == 1

    videos = [
        existing_video,
        Video(
            youtube_id="_vdipCXyrFw",
            published_at=timezone.make_aware(timezone.datetime(2019, 9, 5, 17, 43, 56)),
        ),
    ]

    custom_now = timezone.now()
    with mock.patch.object(client, "fetch_latest") as fetch_latest:
        with mock.patch("subscriptions.utils.crawler.timezone.now") as mock_now:
            mock_now.return_value = custom_now
            fetch_latest.return_value = videos

            crawler = Crawler(client)
            crawler.crawl(user=user)

    db_videos = Video.objects.all()
    assert [v.youtube_id for v in db_videos] == [v.youtube_id for v in videos]
    assert db_videos[0].watched
    assert not db_videos[1].watched
    assert Subscription.objects.get(name="outsidexbox").last_checked == custom_now


@pytest.mark.django_db
@pytest.mark.parametrize(
    "last_checked", [None, timezone.make_aware(timezone.datetime(2019, 9, 1))]
)
def test_crawler_for_single_subscription(client, last_checked, user):
    latest_update = timezone.make_aware(timezone.datetime(2019, 10, 1))

    # Create two subscriptions that have one new video each
    sub = Subscription.objects.create(
        user=user,
        name="outsidexbox",
        youtube_id="UCKk076mm-7JjLxJcFSXIPJA",
        type="ItemType.CHANNEL",
        last_checked=last_checked,
    )

    videos = [Video(youtube_id="123", subscription=sub, published_at=latest_update)]

    custom_now = timezone.now()
    with mock.patch.object(client, "fetch_latest") as fetch_latest:
        with mock.patch("subscriptions.utils.crawler.timezone.now") as mock_now:
            mock_now.return_value = custom_now
            fetch_latest.return_value = videos

            crawler = Crawler(client)
            crawler.crawl_subscription(sub)

    db_videos = Video.objects.all()
    assert len(db_videos) == 1
    assert db_videos[0].youtube_id == "123"
    assert Subscription.objects.get(name="outsidexbox").last_checked == custom_now

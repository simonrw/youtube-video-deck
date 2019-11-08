import logging
from .models import Subscription
from django.utils import timezone
from django.db.utils import IntegrityError

LOGGER = logging.getLogger("ytvd.subscriptions.utils")


class Crawler:
    """
    Given a subscription id and type, crawl the videos for that
    subscription to find any new ones.
    """

    def __init__(self, client):
        self.client = client

    def crawl(self, *, user):
        """
        Go through all of the subscriptions, check for latest videos
        and update
        """
        subscriptions = Subscription.objects.filter(user__username=user.username).all()
        for sub in subscriptions:
            self.crawl_subscription(sub)

    def crawl_subscription(self, sub):
        LOGGER.info("Crawling for subscription %s", sub)
        now = timezone.now()
        if sub.last_checked is None:
            since = now - timezone.timedelta(days=90)
        else:
            since = sub.last_checked

        videos = self.client.fetch_latest(channel_id=sub.youtube_id, since=since)

        for video in videos:
            video.subscription = sub
            try:
                video.save()
            except IntegrityError as e:
                # Video already exists, so do not bother updating, and silently
                # skip this
                continue

        # Finally update the last_checked field
        sub.last_checked = now
        sub.save()

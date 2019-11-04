from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from subscriptions.utils import YoutubeClient, Crawler
from subscriptions.models import Subscription
import os


class Command(BaseCommand):
    help = "Perform ad-hoc crawling"

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--reset",
            action="store_true",
            default=False,
            help="Reset the database to a known state",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            Subscription.objects.all().delete()

            last_checked = timezone.make_aware(timezone.datetime(2019, 9, 1))
            sub = Subscription.objects.create(
                name="outsidexbox",
                youtube_id="UCKk076mm-7JjLxJcFSXIPJA",
                type="ItemType.CHANNEL",
                last_checked=last_checked,
            )

        api_key = os.environ["GOOGLE_API_KEY"]
        client = YoutubeClient(api_key)
        crawler = Crawler(client)

        crawler.crawl()

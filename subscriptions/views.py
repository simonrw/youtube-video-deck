from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .utils import YoutubeClient, ItemType, Crawler
from .models import Subscription, Video
from .forms import SearchForm
import os


YOUTUBE = YoutubeClient(os.environ["GOOGLE_API_KEY"])
CRAWLER = Crawler(YOUTUBE)


@login_required
def index(request):
    subscriptions = Subscription.objects.all()
    return render(request, "subscriptions/index.html", {"subscriptions": subscriptions})


@login_required
def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            term = form.cleaned_data["term"]
            search_items = list(YOUTUBE.search(term=term))
            return render(
                request,
                "subscriptions/search-results.html",
                {
                    "items": search_items,
                    "PLAYLIST": ItemType.PLAYLIST,
                    "CHANNEL": ItemType.CHANNEL,
                },
            )
    else:
        form = SearchForm()

    return render(request, "subscriptions/search.html", {"form": form})


@login_required
def subscribe(request):
    if request.method == "POST":
        item_id = request.POST["item-id"]
        item_type = request.POST["item-type"]
        item_name = request.POST["item-name"]

        sub = Subscription.objects.create(
            name=item_name, youtube_id=item_id, type=ItemType.from_(item_type)
        )

        # XXX: break this out of band?
        CRAWLER.crawl_subscription(sub)

    return redirect("/ytvd/")


@login_required
def mark_subscription_watched(request):
    if request.method == "POST":
        sub_id = request.POST["subscription-id"]
        sub = Subscription.objects.get(id=sub_id)
        for video in sub.video_set.all():
            video.watched = True
            video.save()

    return redirect("/ytvd/")


@login_required
def mark_video_watched(request):
    if request.method == "POST":
        video_id = request.POST["video-id"]
        video = Video.objects.get(id=video_id)
        video.watched = True
        video.save()

    return redirect("/ytvd/")

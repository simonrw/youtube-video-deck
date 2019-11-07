from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.models import User
from .utils import YoutubeClient, ItemType, Crawler
from .models import Subscription, Video
from .forms import SearchForm
import os


YOUTUBE = YoutubeClient(os.environ["GOOGLE_API_KEY"])
CRAWLER = Crawler(YOUTUBE)


@login_required
def index(request):
    # Get the subscriptions ordered by unwatched videos first, followed by name
    current_users_subscriptions = Subscription.objects.filter(
        user__username=request.user
    )
    subscriptions = current_users_subscriptions.annotate(
        unwatched_video_count=Count("video", filter=Q(video__watched=False))
    )
    sorted_subscriptions = subscriptions.order_by("-unwatched_video_count", "name")
    return render(
        request, "subscriptions/index.html", {"subscriptions": sorted_subscriptions}
    )


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

        current_user = User.objects.get(username=request.user)

        sub = Subscription.objects.create(
            user=current_user,
            name=item_name,
            youtube_id=item_id,
            type=ItemType.from_(item_type),
        )

        # XXX: break this out of band?
        CRAWLER.crawl_subscription(sub)

    return redirect("/")


@login_required
def mark_subscription_watched(request):
    if request.method == "POST":
        sub_id = request.POST["subscription-id"]
        sub = Subscription.objects.get(id=sub_id)
        for video in sub.video_set.all():
            video.watched = True
            video.save()

    return redirect("/")


@login_required
def mark_video_watched(request):
    if request.method == "POST":
        video_id = request.POST["video-id"]
        video = Video.objects.get(id=video_id)
        video.watched = True
        video.save()

    return redirect("/")

@login_required
def update_feeds(request):
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        CRAWLER.crawl(user=user)

    return redirect("/")

from django.shortcuts import render
from django.http import HttpResponseRedirect
from .utils import YoutubeClient, ItemType
from .forms import SearchForm
import os


YOUTUBE = YoutubeClient(os.environ["GOOGLE_API_KEY"])


def index(request):
    return render(request, "subscriptions/index.html")


def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            term = form.cleaned_data["term"]
            search_items = list(YOUTUBE.search(term=term))
            print(len(search_items))
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


def results(request):
    return render(request, "subscriptions/search-results.html")

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("search/subscribe", views.subscribe, name="subscribe"),
    path("watched_sub/", views.mark_subscription_watched, name="sub-watched"),
    path("watched_video/", views.mark_video_watched, name="video-watched"),
]
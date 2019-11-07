from django.urls import path
from . import views
from graphene_django.views import GraphQLView

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("search/subscribe", views.subscribe, name="subscribe"),
    path("watched_sub/", views.mark_subscription_watched, name="sub-watched"),
    path("watched_video/", views.mark_video_watched, name="video-watched"),
    path("update_feeds/", views.update_feeds, name="update-feeds"),
    path("graphql/", GraphQLView.as_view(graphiql=True), name="graphql"),
]

import graphene
from graphene_django.types import DjangoObjectType
from .models import Video, Subscription
from django.contrib.auth.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User


class VideoType(DjangoObjectType):
    class Meta:
        model = Video


class SubscriptionType(DjangoObjectType):
    class Meta:
        model = Subscription


class Query(object):
    all_subscriptions = graphene.List(SubscriptionType)
    all_videos = graphene.List(VideoType)
    all_users = graphene.List(UserType)

    def resolve_all_subscriptions(self, info, **kwargs):
        return Subscription.objects.select_related("user").all()

    def resolve_all_videos(self, info, **kwargs):
        return Video.objects.select_related("subscription").all()

    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()

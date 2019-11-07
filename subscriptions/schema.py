import graphene
from graphene import relay
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Video, Subscription
from django.contrib.auth.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        filter_fields = ["username"]
        interfaces = (relay.Node, )


class VideoType(DjangoObjectType):
    class Meta:
        model = Video
        filter_fields = ["watched"]
        interfaces = (relay.Node, )


class SubscriptionType(DjangoObjectType):
    class Meta:
        model = Subscription
        filter_fields = ["name"]
        interfaces = (relay.Node, )


class Query(object):
    # All fetchers
    all_subscriptions = DjangoFilterConnectionField(SubscriptionType)
    all_videos = DjangoFilterConnectionField(VideoType)
    all_users = DjangoFilterConnectionField(UserType)

    # Single fetchers
    user = relay.Node.Field(UserType)
    video = relay.Node.Field(VideoType)
    subscription = relay.Node.Field(SubscriptionType)

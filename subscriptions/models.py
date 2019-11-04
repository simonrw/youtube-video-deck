from django.db import models


class Subscription(models.Model):
    """
    Represents a single subscription for a user

    *Responsibilities*

    * links the subscription ID to a series of videos
    * tracks the last time the subscription was checked for new items
    * stores whether the subscription is a channel or playlist
    """

    name = models.CharField(max_length=255)
    last_checked = models.DateTimeField(null=True)


class Video(models.Model):
    """
    Represents a single video, belonging to a subscription

    *Responsibilities*

    * track whether the user has watched the video
    * store the thumbnail
    * store the full url to video
    """

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    watched = models.BooleanField(default=False)

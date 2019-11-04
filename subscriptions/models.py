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
    youtube_id = models.CharField(max_length=255)
    type = models.CharField(max_length=31)
    last_checked = models.DateTimeField(null=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    """
    Represents a single video, belonging to a subscription

    *Responsibilities*

    * track whether the user has watched the video
    * store the thumbnail
    * store the full url to video
    """

    name = models.CharField(max_length=255)
    thumbnail_url = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    youtube_id = models.CharField(max_length=255)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    watched = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.youtube_id} from {self.subscription}"

from django.contrib import admin

from .models import Subscription, Video


class VideoAdmin(admin.ModelAdmin):
    fields = ["name", "watched"]


class SubscriptionAdmin(admin.ModelAdmin):
    fields = ["user", "name", "last_checked"]


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Video, VideoAdmin)

from django.contrib import admin
from django.contrib.auth import get_user_model
# Register your models here.

from chat.models import Thread, Notification, Message

class NotificationAdmin(admin.ModelAdmin):

    fields = "author", "receiver", "timestamp", "key",
    readonly_fields = "timestamp", "key",
    list_display = ("id", "author")


admin.site.register(get_user_model())
admin.site.register(Thread)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Message)

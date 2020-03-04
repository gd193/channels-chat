from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models import F
# Create your models here.


class CustomUser(AbstractUser):
    count = models.IntegerField(default = 0)

User = get_user_model()

class Thread(models.Model):
    name = models.TextField()
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    def getmembers(self):
        return self.members
    def last_10_messages(self):
        return Message.objects.filter(thread__name__exact=self.name).order_by('-timestamp')[:10]

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.author.username

class Notification(models.Model):
    author = models.ForeignKey(User, related_name='author_notification', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(User, related_name='receiver_notification', on_delete=models.CASCADE)
    key = models.IntegerField(default=0)

    def __hash__(self):
        return hash((self.author.username, self.receiver.username, self.timestamp, self.pk))


@receiver(models.signals.post_save, sender=Notification)
def execute_after_save(sender, instance, created, *args, **kwargs):
    if created:
        user = instance.receiver
        user.count = F('count') + 1
        user.save()

        instance.key = instance.__hash__()
        instance.save()

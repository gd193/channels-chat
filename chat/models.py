from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

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

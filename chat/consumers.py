from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from chat.models  import Message, Thread, Notification
from django.contrib.auth import get_user_model
from channels.exceptions import DenyConnection

User = get_user_model()


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            self.room_name = await self.get_thread_name()
            self.room_group_name = 'chat_%s' % self.room_name

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.channel_layer.group_add(
                self.scope['user'].username,
                self.channel_name,
            )

            await self.accept()

        else:
            self.channel_name = 'anonymous'
            self.room_group_name = 'anonymous'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.close(code=4003)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json['tag'] == 'message':

            message = text_data_json['message']
            username = self.scope['user'].username
            time = await self.save_message(message, username)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                  'type': 'chat_message',
                  'message': message,
                  'user' : username,
                   'timestamp' : time,
                }
            )

            if not('Lobby' in self.room_group_name):
                threadname = await self.get_thread_name()
                other_users = await self.get_other_users_in_thread(threadname)
                for user in other_users:
                    notification_key = await self.save_notification(author=username, receiver=user, timestamp=time)
                    print(notification_key)
                    await self.channel_layer.group_send(
                        user,
                        {
                            'type': 'notification',
                            'user': username,
                            'timestamp' : time,
                            'key' : notification_key,
                        }
                    )
        elif text_data_json['tag'] == 'deleted_notification':
            print(text_data_json)
            author_username = text_data_json['author']
            key = int(text_data_json['key'])
            await self.delete_notification(author_username, key)

        elif text_data_json['tag'] == 'toggling_sidebar' :
            await self.reset_user_count()


    async def chat_message(self, event):
        message = event['message']
        username = event['user']
        time = event['timestamp']

        await self.send(text_data=json.dumps({
            'type' : 'message',
            'message': message,
            'user' : username,
            'timestamp' : time,
        }))

    async def notification(self, event):
        username = event['user']
        time = event['timestamp']
        key = event['key']

        await self.send(text_data=json.dumps({
            'type' : 'notification',
            'user' : username,
            'timestamp' : time,
            'key' : key
        }))

    @database_sync_to_async
    def save_message(self, content, username):
        user = User.objects.filter(username=username)[0]
        thread = Thread.objects.filter(name=self.room_name)[0]
        message = Message(author = user, content = content, thread = thread)
        message.save()
        return message.timestamp.strftime('%y-%m-%d %H:%M')

    @database_sync_to_async
    def save_notification(self, author, receiver, timestamp):
        author = User.objects.get(username=author)
        receiver = User.objects.get(username=receiver)
        notification = Notification(author = author, timestamp = timestamp, receiver = receiver)
        notification.save()
        return notification.__hash__()

    @database_sync_to_async
    def delete_notification(self, author, key):
        notification = Notification.objects.get(key=key)
        if notification.receiver == self.scope['user'] and notification.author.username == author:
            notification.delete()


    @database_sync_to_async
    def get_thread_name(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.scope['url_route']['kwargs'])
        if room_name == 'Lobby':
            return room_name
        username = self.scope['user'].username
        thread = Thread.objects.filter(name__contains=username)
        thread = thread.filter(name__contains=room_name)
        if len(thread) == 1:
            return thread[0].name


    @database_sync_to_async
    def get_other_users_in_thread(self, threadname):
        username = self.scope['user'].username

        thread = Thread.objects.filter(name__exact=threadname)[0]
        users = thread.members
        users = users.exclude(username__exact=username)
        usernames = []
        for user in users:
            usernames.append(user.username)
        return usernames

    @database_sync_to_async
    def reset_user_count(self):
        user = self.scope['user']
        user.count = 0
        user.save()
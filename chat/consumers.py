from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from chat.models  import Message, Thread
from django.contrib.auth import get_user_model

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

            await self.accept()
        else:
            await self.disconnect()

    async def disconnect(self, close_code):
        print(close_code)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
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

    async def chat_message(self, event):
        message = event['message']
        username = event['user']
        time = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'user' : username,
            'timestamp' : time,
        }))

    @database_sync_to_async
    def save_message(self, content, username):
        user = User.objects.filter(username=username)[0]
        thread = Thread.objects.filter(name=self.room_name)[0]
        message = Message(author = user, content = content, thread = thread)
        message.save()
        return message.timestamp.strftime('%y-%m-%d %H:%M')

    @database_sync_to_async
    def get_thread_name(self):
        room_name = self.scope['url_route']['kwargs']['room_name']
        if room_name == 'Lobby':
            return room_name
        username = self.scope['user'].username
        thread = Thread.objects.filter(name__contains=username)
        thread = thread.filter(name__contains=room_name)
        if len(thread) == 1:
            return thread[0].name



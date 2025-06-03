import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import ChatMessage
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_user = self.scope['url_route']['kwargs']['username']
        self.user = self.scope["user"]

        # Create a unique room name (sorted alphabetically to ensure it's shared both ways)
        users = sorted([self.user.username, self.other_user])
        self.room_name = "_".join(users)
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.save_message(self.user, self.other_user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))

    @sync_to_async
    def save_message(self, sender, receiver_username, message):
        receiver = User.objects.get(username=receiver_username)
        ChatMessage.objects.create(user=sender, recipient=receiver, message=message)

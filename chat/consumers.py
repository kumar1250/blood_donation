# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage  # your ChatMessage model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # other username is provided in the URL route (see routing.py)
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            # reject anonymous
            await self.close()
            return

        # Build a consistent room name for two users (order independent)
        users = sorted([self.user.username, self.other_username])
        self.room_name = f"chat_{users[0]}_{users[1]}"
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket (text)
    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        if not message:
            return

        sender_username = self.user.username
        receiver_username = self.other_username

        # Save to DB (sync DB calls must be wrapped)
        await self.save_message(sender_username, receiver_username, message)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',   # handler name -> chat_message
                'message': message,
                'sender': sender_username,
            }
        )

    # Handler for messages sent to the group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))

    @database_sync_to_async
    def save_message(self, sender_username, receiver_username, message):
        try:
            sender = User.objects.get(username=sender_username)
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return None
        return ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)
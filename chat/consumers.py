# chat/consumers.py

import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from .models import Message, ChatRoom

User = get_user_model()

# Asynchronous helpers for database operations
@database_sync_to_async
def get_room(room_name):
    return ChatRoom.objects.get(name=room_name)

@database_sync_to_async
def get_message_history(room):
    # Retrieve the last 50 messages from the room
    messages = room.messages.order_by('-timestamp')[:50]
    return list(messages.values('sender__username', 'content', 'timestamp'))

@database_sync_to_async
def save_message(room, user, content):
    Message.objects.create(room=room, sender=user, content=content)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope["user"]

        if user is None:
            print("user not authenticated")
            await self.close()
            return

        await self.channel_layer.group_add(
            "ManiGroup",
            "ManiChannel",
        )
        await self.accept()
        print(f"{user.first_name} connected successfuly")
        

class ChatConsumer2(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']

        # Reject unauthenticated connections immediately.
        if not user.is_authenticated:
            print("Authentication failed. Closing connection.")
            await self.close()
            return #to stop continuing `connect` function

        # Define room-related attributes at the start.
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Check if the room exists. If not, close the connection.
        try:
            self.room_obj = await get_room(self.room_name)
        except ChatRoom.DoesNotExist:
            print(f"Chat room '{self.room_name}' does not exist.")
            await self.close()
            return  # Use a return to exit

        # Add the user to the group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the connection.
        await self.accept()
        print(f"User {user.username} connected to room {self.room_name}")

        # Fetch and send message history.
        history = await get_message_history(self.room_obj)
        await self.send_json({
            'type': 'chat.history',
            'messages': history
        })

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.is_authenticated:
            # Remove the user from the room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {user.username} disconnected from room {self.room_name}")

    async def receive_json(self, content, **kwargs):
        user = self.scope['user']
        if user.is_authenticated:
            message = content.get('message')
            if message:
                # Save the message to the database
                await save_message(self.room_obj, user, message)

                # Broadcast the message to the group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat.message',
                        'message': message,
                        'username': user.username,
                    }
                )
        else:
            await self.send_json({"error": "Authentication required."})

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send the message back to the client
        await self.send_json({
            'type': 'chat.message',
            'username': username,
            'content': message,
        })
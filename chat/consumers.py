# chat/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from .services import get_room, save_message, is_throttled
from .models import Message, ChatRoom
from channels.db import database_sync_to_async
from chat import services


User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope["user"]

        #check if user is authenticated
        if user is None:
            print("user not authenticated")
            await self.close()
            return
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        try:
            self.room_obj = await get_room(self.room_name)
        except ChatRoom.DoesNotExist:
            print(f"Chat room {self.room_name} does not exists")
            await self.close()
            return
        
        #check if user is a participant of the chat room
        is_participant = await services.is_participant(user, self.room_obj)
        if not is_participant:
            print("user is not a participant")
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()
        print(f"{user.first_name} connected successfuly to {self.room_name}")

    async def disconnect(self, close_code):
        print(f"close code -> {close_code}")
        user = self.scope["user"]
        if user and user.is_authenticated:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"User {user.username} disconnected from room {self.room_name}")

    async def receive_json(self, content, **kwargs):
        user = self.scope["user"]
        if user.is_authenticated:
            message = content.get("message")
            if message:
                #check if user is a participant of the chat room
                is_participant = await services.is_participant(user, self.room_obj)
                if not is_participant:
                    print("user is not a participant")
                    await self.close()
                    return
                
                #throttle check
                print(is_throttled(user), "--------------")
                is_user_throttled, next_try = is_throttled(user)
                if is_user_throttled:

                    await self.send_json({
                        "error" : f"Rate limit exceeded. Try again in {next_try} seconds",
                        "next_try" : next_try
                    })
                    return
                
                await save_message(self.room_obj, user, message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type" : "chat.message",
                        "message" : message,
                        "username" : user.username
                    }
                )
        else:
            await self.send_json({"error":"Authentication required."})

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send_json({
            'type' : 'chat.message',
            'username' : username,
            'content' : message
        })
            
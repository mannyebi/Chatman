from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
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
            self.room_obj = await services.get_room(self.room_name)
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

            #check if user is a participant of the chat room
            is_participant = await services.is_participant(user, self.room_obj)
            if not is_participant:
                print("user is not a participant")
                await self.close()
                return
            
            #throttle check
            is_user_throttled, next_try = services.is_throttled(user)
            if is_user_throttled:

                await self.send_json({
                    "error" : f"Rate limit exceeded. Try again in {next_try} seconds",
                    "next_try" : next_try
                })
                return

            #check and validate message type.
            type = content.get("type")
            
            if type == "chat.message":
                text = content.get("text", None)
                await self.handle_chat_message(user, text)
            elif type == "chat.media":
                files_pk = content.get("files_pk", [])
                caption = content.get("caption", None)
                await self.handle_chat_media(user, caption, files_pk)
            elif type == "file.message":
                pass
        else:
            await self.send_json({"error":"Authentication required."})
            return
        
    async def handle_chat_message(self, user, text):
        print("aa")
        if not text or len(text.strip()) == 0:
            await self.send_json({
                "type" : "error",
                "code" : 400,
                "message" : "Message text is missing or invalid."
            })
            return

        await services.save_message(self.room_obj, user, text=text)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type":"chat.message",
                "username": user.username,
                "text": text,
            }
        )

    async def handle_chat_media(self, user, caption, files_pk):
        if not caption or len(caption.strip()) == 0 or len(files_pk) == 0:
            await self.send_json({
                "type" : "error",
                "code" : 400,
                "message" : "Message caption or file/files is/are missing or invalid."
            })

        message = await services.save_message(self.room_obj, user, text=caption, file_pks=files_pk)
        files_data = [
            {
                "url" : file_obj.file.url,
                "filename" : file_obj.filename,
                "file_type" : file_obj.content_type,
            }
            for file_obj in await database_sync_to_async(list)(message.files.all())
        ]
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type" : "chat.media",
                "username" : user.username,
                "files" : files_data,
                "caption" : caption,
            }
        )
    

    async def chat_message(self, event):
        """
        Handler for messages broadcasted to the group.
        Takes the event and sends it to the client.
        """
        # The 'event' dictionary contains the data from group_send
        await self.send_json({
            "type": "chat.message",
            "username": event["username"],
            "text": event["text"]
        })

    async def chat_media(self, event):
        """
        Handler for media messages broadcasted to the group.
        """
        await self.send_json({
            "type": "chat.media",
            "username": event["username"],
            "files": event["files"],
            "caption": event["caption"]
        })

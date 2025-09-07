from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message, ChatRoom
from channels.db import database_sync_to_async
from chat import services
from datetime import datetime

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        user = self.scope["user"]

        #check if user is authenticated
        if not user:
            print("user not authenticated")
            await self.close()
            return
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        try:
            self.room_obj = await services.get_room(self.room_name)
        except ChatRoom.DoesNotExist:
            self.room_obj = await services.create_private_chat_with_chatroom_name(self.room_name)
        
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
                file_pks = content.get("file_pks", [])
                caption = content.get("caption", None)
                await self.handle_chat_media(user, caption, file_pks)
            elif type == "file.message":
                file_pks = content.get("file_pks", [])
                await self.handle_file_message(user, file_pks)
            elif type == "typing.status":
                await self.handle_typing_status(user)

            elif type == "delete.message":
                #TODO: ensure the user can only delete a message from it self.
                id = content.get("message_id", None)
                await self.handle_message_delete(id)

            elif type == "transfer.notification":
                print("hi i've called ")
                transfer_id = content.get("transfer_id")
                receiver_username = content.get("receiver_username")
                amount = content.get("amount")
                description = content.get("description")
                created_at = content.get("created_at")
                
                await self.handle_transfer_notification(transfer_id, user.username, receiver_username, amount, description, created_at)

        else:
            await self.send_json({"error":"Authentication required."})
            return
        
    async def handle_chat_message(self, user, text):
        
        if not text or len(text.strip()) == 0:
            await self.send_json({
                "type" : "error",
                "code" : 400,
                "message" : "Message text is missing or invalid."
            })
            return

        message_obj = await services.save_message(self.room_obj, user, text=text)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type":"chat.message",
                "username": user.username,
                "id": message_obj.id,
                "text": text,
            }
        )

    async def handle_chat_media(self, user, caption, file_pks):
        if not caption or len(caption.strip()) == 0 or len(file_pks) == 0:
            await self.send_json({
                "type" : "error",
                "code" : 400,
                "message" : "Message caption or file/files is/are missing or invalid."
            })

        message = await services.save_message(self.room_obj, user, text=caption, file_pks=file_pks)
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

    async def handle_file_message(self, user, file_pks):
        if not file_pks:
            await self.send_json({
                "type" : "error",
                "code" : 400,
                "message" : "file/files are missing or invalid."
            })
        message = await services.save_message(self.room_obj, user, file_pks=file_pks)
        file_data = [
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
                "type" : "file.message",
                "username" : user.username,
                "files" : file_data,
                "timestamp" : message.timestamp.isoformat(),
                "id" : message.id
            }
        )
    
    async def handle_typing_status(self, user):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type" : "typing.status",
                "username" : user.username 
            }
        )

    async def handle_message_delete(self, id):
        try:
            await services.delete_message(id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type" : "delete.message",
                    "message_id" : id
                }
            )
        except Exception as e:
            print(e)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type" : "delete.message",
                    "message_id" : None
                }
            )

    async def handle_transfer_notification(self, transfer_id, sender_username, receiver_username, amount, description, created_at):
        user = self.scope['user']
        try:
            message = await services.save_message(self.room_obj, user, text="", transaction_id=transfer_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type" : "transfer.notification",
                    "transfer_id" : transfer_id,
                    "sender_username" : sender_username,
                    "receiver_username" : receiver_username,
                    "amount" : amount,
                    "description" : description,
                    "created_at" : created_at,
                    "id" : message.id
                }
            )
        except Exception as e:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type" : "transfer.notification",
                    "error" : f"{e}",
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
            "timestamp": datetime.now().isoformat(),
            "id": event["id"],
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

    async def file_message(self, event):
        await self.send_json({
            "type" : "file.message",
            "username" : event['username'],
            "files" : event['files'],
            "timestamp" : event['timestamp'],
            "id" : event['id']
        })

    async def typing_status(self, event):
        await self.send_json({
            "type" : "typing.status",
            "username" : event['username']
        })

    async def delete_message(self, event):
        await self.send_json({
            "type" : "delete.message",
            "message_id": event["message_id"]
        })

    async def transfer_notification(self, event):
        print("callllled 1")
        await self.send_json({
            "type" :"transfer.notification",
            "username": event["sender_username"],
            "transaction": {
                "id": event["transfer_id"],
                "amount":event["amount"]
            },
            "timestamp": event["created_at"],
            "id": event['id']
        })
    

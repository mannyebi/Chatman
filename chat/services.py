from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Message, ChatRoom


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

@database_sync_to_async
def is_participant(user, room):
    """check if the give user is a participant of this chatroom.
        return true if the user is a participant, False otherwise.  
    """
    return room.participants.filter(pk=f"{user.id}").exists()
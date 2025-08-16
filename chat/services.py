from channels.db import database_sync_to_async
from .models import Message, ChatRoom, File
from django.core.cache import cache
import time
from django.db.models import Q


# Asynchronous helpers for database operations
@database_sync_to_async
def get_room(room_name):
    return ChatRoom.objects.get(name=room_name)

@database_sync_to_async
def get_message_history(room):
    # Retrieve the last 50 messages from the room
    messages = room.messages.order_by('-timestamp')[:50]
    return list(messages.values('sender__username', 'text', 'timestamp'))

@database_sync_to_async
def save_message(room, user, text="", file_pks=[]):
    message = Message.objects.create(
        room=room, 
        sender=user, 
        text=text 
    )

    if file_pks:
        files_queryset = File.objects.filter(
            pk__in=file_pks,
            uploader = user
        )
        message.files.set(files_queryset)
    return message

@database_sync_to_async
def is_participant(user, room):
    """check if the give user is a participant of this chatroom.
        return true if the user is a participant, False otherwise.  
    """
    return room.participants.filter(pk=f"{user.id}").exists()

def is_throttled(user, window=60, limit=60):
    """return True, if user has been sent more message

    user: User obj.
    window : the time range in seconds.
    limit : the maximum allowed message.
    """
    user_key = f"chat_throttle_{user.id}"

    timestamps = cache.get(user_key, []) #get previous stored timestamps
    now = time.time()

    #filter expired (more than `window`) timestamps
    timestamps = [ts for ts in timestamps if now - ts < window]

    if len(timestamps) > limit:
        try_again_in = window - (now - timestamps[-1]) if timestamps else window
        return True, try_again_in
    
    timestamps.append(now)
    cache.set(user_key, timestamps, timeout=window)
    return False, 0

def save_file(uploader, file, filename, content_type):
    """save a file record in database with the given data
    """
    return File.objects.create(uploader=uploader, file=file, filename=filename, content_type=content_type)
    
def get_or_create_private_chat(user1, user2):

    try:
        user1_id = int(user1.id)
        user2_id = int(user2.id)
    except ValueError as ve:
        raise

    name = f"pv_{max(user2_id, user1_id)}{min(user1_id,user2_id)}"
    chat, created = ChatRoom.objects.filter(Q(is_group=False) & Q(name=name)).get_or_create(defaults={"is_group":False, "name":name})

    if created:
        chat.participants.add(user1, user2)
    
    return chat, created
    
def get_or_create_group_chat(group_name, participants:list, group_display_name=""):
    
    chat, created = ChatRoom.objects.filter(Q(is_group=True) & Q(name=group_name)).get_or_create(defaults={"is_group":True, "name":group_name, "display_name":group_display_name})

    if created:
        chat.participants.add(*participants)

    return chat, created
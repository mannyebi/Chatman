from channels.db import database_sync_to_async
from .models import Message, ChatRoom, File, ChatMembership
from django.core.cache import cache
import time
from django.db.models import Q
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from wallet.models import Transaction

User = get_user_model()


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
def save_message(room, user, text="", file_pks=[], transaction_id=None):
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

    if transaction_id:
        try:
            transaction = get_object_or_404(Transaction, id=transaction_id)
            message.transaction = transaction
            message.save()
        except Exception as e:
            print(e)
            raise

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

def save_file(uploader, file, content_type, filename):
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
    
def get_or_create_group_chat(group_name, group_creator, participants:list, group_display_name=""):
    """
    Retrieves or creates a group chat and manages its participants.
    """
    try:
        with transaction.atomic():
            # 1. Get or create the group object. This handles the unique constraint.
            chatroom, created = ChatRoom.objects.get_or_create(
                is_group=True,
                name=group_name,
                defaults={"display_name": group_display_name}
            )

            if created:
                # 2. Only if a new chatroom was created, add the participants.
                # First, add the creator as an 'admin'
                ChatMembership.objects.create(
                    user=group_creator,
                    chatroom=chatroom,
                    role="owner"
                )

                # 3. Add other participants. Use a simple loop to avoid
                # potential issues with bulk_create.
                other_participants = [p for p in participants if p != group_creator]
                for p in other_participants:
                    ChatMembership.objects.create(
                        user=p, 
                        chatroom=chatroom, 
                        role='participant'
                    )

        # Return the chatroom object and the 'created' flag to the caller.
        return chatroom, created
    except Exception as e:
        # A different error occurred (e.g., database connection issue).
        # Re-raise the exception to be handled by the calling view.
        raise


def has_permission(membership, permission):
    """check if `user` in `chat` has a specific permission or not, if yes return True, otherwise False.
    """
    ROLE_PERMISSIONS = {
    "owner": {"add_members", "remove_members", "promote_admin", "delete_group"},
    "admin": {"add_members", "remove_members"},
    "participant": {"send_message"},
    }   
    return permission in ROLE_PERMISSIONS[membership.role]


def delete_group(group):
    """delete the give group
    """
    try:
        group.delete()
    except Exception:
        raise


def controll_memebership(membership, role=None):
    """controll membership (delete, promote, demote).
    """
    try:
        if role:
            membership.role = role
            membership.save()
    except Exception as e:
        raise


def handle_delete_group(chat):
    """handle group deleting.
    """
    try:
        delete_group(chat)
        return Response({"message":"group deleted successfuly"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"error":"an error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def handle_promote_user_to_admin(selected_admins):
    try:
        for selected_admin in selected_admins:
            controll_memebership(selected_admin, "admin")
        return Response({"message":"user promoted successfuly"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"error":"an error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def handler_removing_members(chat, users):
    removing_ids = set()
    for member_id in users.split(","):
        #ensure string is not empty
        stripped_memeber_id = member_id.strip()
        try:
            int_member_id = int(stripped_memeber_id)
        except Exception:
            return Response({"message":"one or more of the inputed users are not valid."}, status=status.HTTP_400_BAD_REQUEST)
        if stripped_memeber_id:
            removing_ids.add(int_member_id)

    try:
        removing_users = ChatMembership.objects.filter(Q(chatroom=chat) & Q(user_id__in=removing_ids))
    except ValueError as ve:
        print(ve)
        return Response({"message":"the inputed users are not valid."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        for removing_user in removing_users:
            if removing_user.role != "owner":
                removing_user.delete()
        return Response({"message":"deleted successfuly."}, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        raise

def handle_add_member(chat, user_ids):
    try:
        users = set()

        for user_id in user_ids.split(","):
            stripped_user_id = user_id.strip()
            if stripped_user_id:
                try:
                    int_user_id = int(stripped_user_id)
                except Exception:
                    return Response({"error":"one or more of the inputed users are invalid."}, status=status.HTTP_400_BAD_REQUEST)
                
                user_obj = get_object_or_404(User, id=int_user_id)
                users.add(user_obj)
            
        for user in users:
            print(user)
            ChatMembership.objects.get_or_create(user=user, chatroom=chat,defaults={"user":user, "chatroom":chat})

        return Response({"message":"added successfuly"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        raise


def fetch_messages(chatroom, chunk=20):
    """fetch `chunk` numbers of messages in `chatroom`
    """
    try:
        return Message.objects.filter(room=chatroom).all().order_by('timestamp')[:chunk]
    except Exception as e:
        print(e)
        raise

@database_sync_to_async
def delete_message(id):
    """delete message with pk = id
    """
    message = Message.objects.get(id=id)
    try:
        message.delete()
    except Message.DoesNotExist as e:
        print(e)
        raise
    except Exception as excep:
        print(excep)
        raise
    


def fetch_chat_list(user, chunk=20):
    """return any chatroom which `user` is a participant in it
    """
    try:
        return user.chat_rooms.all()
    except Exception as e:
        print(e)
        raise
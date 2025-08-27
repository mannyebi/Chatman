from django.urls import path
from chat.views import UploadFile, CreatePrivateChatRoom, CreateGroupChatRoom, HandleGroupChat, FetchChatroomMessages
urlpatterns = [
    path("upload/", UploadFile.as_view(), name="upload"),
    path("create-private-chat-room/", CreatePrivateChatRoom.as_view(), name="create_private_chat_room"),
    path("create-group-chat-room/", CreateGroupChatRoom.as_view(), name="create_group_chat_room"),
    path("handle-group-chat-room/", HandleGroupChat.as_view(), name="handle_group_chat_room"),
    path("fetch-messages/", FetchChatroomMessages.as_view(), name="fetch-chatroom-messages"),
]
from django.urls import path
from chat.views import *


urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('private_chat/<str:other_user_id>', PrivateChatRoom.as_view(), name="private_chat_room"),
]
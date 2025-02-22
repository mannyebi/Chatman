from django.urls import re_path, path
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/private_chat/<int:other_user_id>/", ChatConsumer.as_asgi())
]
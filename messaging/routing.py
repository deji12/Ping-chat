from django.urls import path
from .consumers import ChatConsumer, ChatListConsumer

websocket_urlpatterns = [
    path('chat/<int:friendship_id>/', ChatConsumer.as_asgi()),
    path('chat/', ChatListConsumer.as_asgi())
]
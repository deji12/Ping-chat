from django.urls import path
from .views import chat_list, send_image_message

urlpatterns = [
	path('', chat_list, name='chat'),
	path('<int:friendship_id>/', chat_list, name='chat_detail'),
	path('image-message/<int:friendship_id>/', send_image_message, name='send_image_message')
]
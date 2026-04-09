from django.urls import path
from .views import chat_list, send_image_message, home_page

urlpatterns = [
	path('', home_page, name='home_page'),
	path('chat/', chat_list, name='chat'),
	path('chat/<int:friendship_id>/', chat_list, name='chat_detail'),
	path('chat/image-message/<int:friendship_id>/', send_image_message, name='send_image_message')
]
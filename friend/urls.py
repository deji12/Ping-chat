from django.urls import path
from .views import (
	add_friend, friend_requests, update_friend_request_status, 
	friends, delete_friendship
)

urlpatterns = [
	path('add/<str:friend_username>/', add_friend, name='add_friend'),
	path('delete/<str:friendship_id>/', delete_friendship, name='delete_friend'),
	path('requests/', friend_requests, name='friend_requests'),
	path('update-request-status/<int:friend_request_id>/', update_friend_request_status, name='update_friend_request_status'),
	path('list/', friends, name='friends'),
]
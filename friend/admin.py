from django.contrib import admin
from .models import Friendship

class FriendshipAdmin(admin.ModelAdmin):
	list_display = ['from_user', 'to_user', 'status', 'created_at', 'friend_request_accept_at', 'last_message_sent_when']

admin.site.register(Friendship, FriendshipAdmin)

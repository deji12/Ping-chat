from django.contrib import admin
from .models import Message

class MessageAdmin(admin.ModelAdmin):
	list_display = ['friendship', 'sent_by', 'sent_at']

admin.site.register(Message, MessageAdmin)
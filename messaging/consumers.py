import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
from friend.models import Friendship, FriendshipStatus
from user.models import User
from django.db.models import Q
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncWebsocketConsumer):

	async def connect(self):
		self.user = self.scope['user']
		if self.user.is_anonymous:
			await self.close(code=4001)  # Unauthorized
			return

		friendship_id = self.scope['url_route']['kwargs']['friendship_id']
		self.friendship = await self.get_friendship(friendship_id) 
		if not self.friendship:
			await self.close(code=4002)
			return

		if not self.is_user_allowed():
			await self.close(code=4002)
			return

		self.room_name = f"room_{friendship_id}"
		await self.channel_layer.group_add(self.room_name, self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(self.room_name, self.channel_name)

	async def receive(self, text_data):
	    data = json.loads(text_data)
	    sender_id = data.get('sender_id')
	    message_type = data.get('message_type')
	    reply_to_id = data.get('reply_to_id')  # ✅ NEW

	    print(data)

	    if message_type == 'text':
	        message = data.get('message')
	        created_msg = await self.create_message(sender_id, message, reply_to_id)  # ✅ pass reply
	        
	        # Build reply preview to broadcast
	        reply_preview = None
	        if reply_to_id:
	            reply_preview = await self.get_reply_preview(reply_to_id)

	        payload = {
	            'type': 'send_message',
	            'data': {
	                'message_type': message_type,
	                'sender_id': sender_id,
	                'message': message,
	                'message_id': created_msg.id,
	                'sent_at': timezone.now().isoformat(),
	                'recipient_id': str(self.get_recipient_user_id()),
	                'friendship_id': f'{self.friendship.id}',
	                'reply_preview': reply_preview,  # ✅ NEW
	            }
	        }
	        await self.channel_layer.group_send(self.room_name, payload)
	    else:
	        await self.send(text_data=json.dumps({'error': 'Invalid message_type'}))
	        return

	async def send_message(self, event):
	    data = event["data"]
	    recipient_user_id = data['recipient_id']

	    # Forward to recipient's personal chat list group
	    await self.channel_layer.group_send(
	        f'chat_list_{recipient_user_id}',
	        event
	    )

	    # Send to the current WebSocket connection
	    await self.send(text_data=json.dumps({"data": data}))

	@database_sync_to_async
	def get_friendship(self, friendship_id):
		return Friendship.objects.filter(
			id=friendship_id,
			status=FriendshipStatus.accepted
		).select_related('from_user', 'to_user').first()

	def get_recipient_user_id(self):
		return self.friendship.get_friend(self.user).id

	def is_user_allowed(self):
		return self.user.id == self.friendship.from_user_id or self.user.id == self.friendship.to_user_id

	@database_sync_to_async
	def create_message(self, sender_id, message, reply_to_id=None):
	    reply_to = None
	    if reply_to_id:
	        try:
	            reply_to = Message.objects.get(id=reply_to_id)
	        except Message.DoesNotExist:
	            pass

	    msg = Message.objects.create(
	        friendship=self.friendship,
	        text_content=message,
	        sent_by=self.user if self.user.id == int(sender_id) else User.objects.get(id=sender_id),
	        reply_to=reply_to,  # ✅ NEW
	    )
	    self.friendship.number_of_messages_sent += 1
	    self.friendship.save()
	    return msg

	@database_sync_to_async
	def get_reply_preview(self, reply_to_id):
	    try:
	        msg = Message.objects.select_related('sent_by').get(id=reply_to_id)
	        return {
	            'sender_name': msg.sent_by.get_full_name() or msg.sent_by.username,
	            'text': (msg.text_content or '')[:80],
	            'has_image': bool(msg.image),
	            'image_url': msg.image_url() if msg.image else None,
	            'id': msg.id,
	        }
	    except Message.DoesNotExist:
	        return None

class ChatListConsumer(AsyncWebsocketConsumer):

	async def connect(self):
		self.user = self.scope['user']
		if self.user.is_anonymous:
			await self.close(code=4001)  # Unauthorized
			return

		self.room_name = f"chat_list_{self.user.id}"
		await self.channel_layer.group_add(self.room_name, self.channel_name)
		await self.accept()

	async def disconnect(self, close_code):
		await self.channel_layer.group_discard(self.room_name, self.channel_name)

	async def send_message(self, event):
		data = event["data"]
		await self.send(text_data=json.dumps({"data": data}))
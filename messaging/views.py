from django.shortcuts import render, redirect
from .models import Message
from django.contrib.auth.decorators import login_required
from friend.models import Friendship, FriendshipStatus
from django.db.models import Q
from django.contrib import messages
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.http import JsonResponse

def home_page(request):

	return render(request, 'index.html')

@login_required
def chat_list(request, friendship_id=None):

	user = request.user
	user_friendships = Friendship.objects.filter(
		Q(to_user=user) | Q(from_user=user),
		status=FriendshipStatus.accepted
	).select_related('from_user', 'to_user').order_by('-last_message_sent_when')


	context = {
		'user_friendships': user_friendships,
		'default_profile_image': settings.DEFAULT_USER_PROFILE_IMAGE
	}

	if friendship_id:
		friendship = Friendship.objects.filter(
			Q(to_user=user) | Q(from_user=user),
			status=FriendshipStatus.accepted,
			id=friendship_id
		).select_related('from_user', 'to_user').prefetch_related('messages').first()

		if not friendship:
			messages.error(request, 'Invalid friendship id')
			return redirect(request.META.get('HTTP_REFERER', '/'))

		context['friendship'] = friendship
		context['friendship_messages'] = friendship.get_messages()
		context['friend'] = friendship.get_friend(user)

	return render(request, 'chat/chat.html', context)

@login_required
def send_image_message(request, friendship_id):

	user = request.user
	friendship = Friendship.objects.filter(
		Q(to_user=user) | Q(from_user=user),
		status=FriendshipStatus.accepted,
		id=friendship_id
	).select_related('from_user', 'to_user').first()

	if not friendship:
		messages.error(request, 'Invalid friendship id')
		return redirect(request.META.get('HTTP_REFERER', '/'))

	if request.method == 'POST':
		image = request.FILES.get('image')
		text_message = request.POST.get('text_message')

		message = Message.objects.create(
			friendship=friendship,
			sent_by=user,
			image=image,
			text_content=text_message
		)

		# broadcast the image links to the chat room
		channel_layer = get_channel_layer()
		async_to_sync(channel_layer.group_send)(
			f'room_{friendship_id}',
			{
				'type': 'send_message',
				'data': {
					'message_type': 'image_text',
					'sender_id': f'{user.id}',
					'message': text_message or '',
					'image_url': message.image_url(),
					'sent_at': timezone.now().isoformat(),
					'recipient_id': f'{friendship.get_friend(user).id}',
					'friendship_id': f'{friendship.id}'
				}
			}
		)
		return JsonResponse({'status': 'ok'}, status=200)

	return JsonResponse({'error': 'Method not allowed'}, status=405)
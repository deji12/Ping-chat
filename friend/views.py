from django.shortcuts import render, redirect
from .models import Friendship, FriendshipStatus
from user.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

@login_required
def add_friend(request, friend_username):

	user = request.user

	if friend_username == user.username:
		messages.error(request, "You can't create a friendship with yourself")
		return redirect(request.META.get('HTTP_REFERER', '/'))

	try:
		friend = User.objects.get(username=friend_username)
	except User.DoesNotExist:
		messages.error(request, 'No user with that username exists')
		return redirect(request.META.get('HTTP_REFERER', '/'))

	friendship = Friendship.objects.filter(
		Q(from_user=user, to_user=friend) |
		Q(from_user=friend, to_user=user),
	).distinct().exclude(status=FriendshipStatus.deleted)

	# check to see if the recipient of this request already sent a friend request to user
	pending_acceptance = friendship.filter(status=FriendshipStatus.pending).first()
	if pending_acceptance and pending_acceptance.sender != user:
		pending_acceptance.status = FriendshipStatus.accepted
		pending_acceptance.save(update_fields=['status'])
		messages.success(request, 'Friendship created successfully')

	else:
		if not friendship:
			friendship = Friendship.objects.create(
				from_user = user,
				to_user = friend
			)
			messages.success(request, 'Friend request sent successfully')

		else:
			messages.error(request, f'You are already friends with {friend_username}')	
	return redirect(reverse('profile', kwargs={'username': friend_username}))

@login_required
def friend_requests(request):

	pending_friend_requests = Friendship.objects.filter(
		to_user=request.user,
		status = FriendshipStatus.pending 
	).select_related('from_user')

	context = {
		'friend_requests': pending_friend_requests
	}
	return render(request, 'friends/requests.html', context)

@login_required
def update_friend_request_status(request, friend_request_id):

	user = request.user
	friend_request = Friendship.objects.filter(
		id=friend_request_id,
		to_user=user,
		status=FriendshipStatus.pending
	).select_related('to_user').first()

	if not friend_request:
		messages.error(request, 'Invalid friend request id')
		return redirect(request.META.get('HTTP_REFERER', '/'))

	status = request.GET.get('status')
	from_user = friend_request.from_user

	if status == FriendshipStatus.accepted:
		friend_request.friend_request_accept_at = timezone.now()
		friend_request.status = FriendshipStatus.accepted
		friend_request.save(update_fields=['friend_request_accept_at', 'status'])

		# update friend count
		user.number_of_friends += 1
		user.save(update_fields=['number_of_friends'])

		from_user.number_of_friends += 1
		from_user.save(update_fields=['number_of_friends'])

		messages.success(request, 'Friend request accepted!')

	elif status == FriendshipStatus.declined:
		friend_request.delete()
		messages.success(request, 'Friend request declined')

	else:
		messages.error(request, 'Invalid friendship status provided')
		
	return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def friends(request):

	user = request.user
	friends = Friendship.objects.filter(
		Q(to_user=user) | Q(from_user=user),
		status=FriendshipStatus.accepted
	).select_related('from_user', 'to_user')

	context = {
		'friends': friends
	}
	return render(request, 'friends/friends.html',context)

@login_required
def delete_friendship(request, friendship_id):

	user = request.user
	friendship = Friendship.objects.filter(
		Q(to_user=user) | Q(from_user=user),
		id=friendship_id,
		status=FriendshipStatus.accepted
	).first()

	if not friendship:
		messages.error(request, 'Friendship not found')
		return redirect(request.META.get('HTTP_REFERER', '/'))

	friendship.status = FriendshipStatus.deleted
	friendship.save(update_fields=['status'])

	messages.success(request, 'Friendship deleted successfully')
	return redirect('friends')
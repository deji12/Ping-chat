from django.shortcuts import render, redirect
from .models import User, PasswordResetCode
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import validate_registration_data, validate_passwords, is_valid_email
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import Q
from friend.models import Friendship

def register_user(request):
	user = request.user
	if user.is_authenticated:
		return redirect(reverse('profile', kwargs={'username': user.username}))

	if request.method == 'POST':
		username = request.POST.get('username')
		email = request.POST.get('email')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		password = request.POST.get('password')
		confirm_password = request.POST.get('confirm_password')

		errors = validate_registration_data(
			username = username,
			email = email,
			first_name = first_name,
			last_name = last_name,
			password = password,
			confirm_password = confirm_password
		)

		if errors:
			register_url = f"{reverse('register_user')}?email={email}&first_name={first_name}&last_name={last_name}&username={username}"  
			for error_message in errors:
				messages.error(request, error_message)
			return redirect(register_url)	

		user = User.objects.create_user(
			username = username,
			email = email,
			first_name = first_name,
			last_name = last_name,
			password = password
		)

		messages.success(request, 'Account created successfully')
		return redirect('login_user')

	return render(request, 'user/auth/register.html')

def login_user(request):
	user = request.user
	if user.is_authenticated:
		return redirect(reverse('profile', kwargs={'username': user.username}))

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		if not (username and password):
			messages.error(request, 'Username and password are required')
			return redirect('login_user')

		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect(reverse('profile', kwargs={'username': user.username}))
		
		messages.error(request, 'Invalid username or password provided')
		return redirect('login_user')

	return render(request, 'user/auth/login.html')

def logout_user(request):
	logout(request)
	return redirect('login_user')

def forgot_password(request):
	user = request.user
	if user.is_authenticated:
		return redirect(reverse('profile', kwargs={'username': user.username}))

	if request.method == 'POST':
		email = request.POST.get('email')

		user = User.objects.filter(email=email).first()
		if not user:
			messages.error(request, 'No user with that email exists')
			return redirect('forgot_password')

		# delete potential old reset codes
		PasswordResetCode.objects.filter(user=user).delete()

		password_reset = PasswordResetCode.objects.create(user=user)
		user.send_password_reset_email(
			request, 
			request.build_absolute_uri(reverse('reset_password', kwargs={'reset_id': password_reset.reset_id})),
			password_reset.reset_id
		)

		return redirect(f"{reverse('forgot_password')}?reset_email_sent=True&email={email}")

	return render(request, 'user/auth/forgot-password.html')

def reset_password(request, reset_id):
	user = request.user
	if user.is_authenticated:
		return redirect(reverse('profile', kwargs={'username': user.username}))

	try:
		reset_id = PasswordResetCode.objects.get(reset_id=reset_id)
	except (PasswordResetCode.DoesNotExist, ValidationError):
		messages.error(request, 'Invalid reset link')
		return redirect('login_user')

	if request.method == 'POST':

		if reset_id.has_expired():
			reset_id.delete()
			messages.error(request, 'Reset link has expired')
			return redirect('login_user')

		password = request.POST.get('password')
		confirm_password = request.POST.get('confirm_password')

		errors = validate_passwords(password, confirm_password)
		if errors:
			for error_message in errors:
				messages.error(request, error_message)
			return redirect('reset_password')

		user = reset_id.user
		user.set_password(password)
		user.save()

		reset_id.delete()

		messages.success(request, 'Password changed successfully')
		return redirect('login_user')

	return render(request, 'user/auth/reset-password.html')

@login_required
def profile_setting(request):
	user = request.user

	if request.method == 'POST':
		profile_image = request.FILES.get('profile_image')
		username = request.POST.get('username')
		email = request.POST.get('email')
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		bio = request.POST.get('bio')
		current_password = request.POST.get('current_password')
		new_password = request.POST.get('password')
		confirm_new_password = request.POST.get('confirm_password')

		if not (username and email):
			messages.error(request, 'Username and email are required')
			return redirect('profile_setting')

		if not is_valid_email(email):
			messages.error(request, 'Invalid email entered')
			return redirect('profile_setting')

		user.username = username
		user.email = email
		user.first_name = first_name
		user.last_name = last_name
		user.bio = bio

		if profile_image:
			user.profile_image = profile_image

		if (current_password and new_password and confirm_new_password):
			if user.check_password(current_password):
				if len(new_password) < 6:
					messages.error(request, 'Password must be at least 6 characters long')
					return redirect('profile_setting')
				
				if new_password != confirm_password:
					messages.error(request, 'Passwords do not match')
					return redirect('profile_setting')

				user.set_password(new_password)
			else:
				messages.error(request, 'Invalid current password entered')
				return redirect('profile_setting')	

		user.save()
		messages.success(request, 'Profile updated')
		return redirect('profile')

	return render(request, 'user/profile/profile-setting.html')

@login_required
def profile(request, username):

	user_account = request.user
	friendship = None

	if user_account.username != username:
		try:
			user_account = User.objects.get(username=username)

			# search for friendship
			friendship = Friendship.objects.filter(
				Q(from_user=request.user, to_user=user_account) |
				Q(from_user=user_account, to_user=request.user)
			).distinct().first()

		except User.DoesNotExist:
			messages.error(request, 'No user with that email exists')
			return redirect('search_users')

	context = {
		'username': username,
		'user_account': user_account,
		'friendship': friendship
	}
	return render(request, 'user/profile/profile.html', context)

@login_required
def search_users(request):

	context = {}
	if request.method == 'POST':
		search = request.POST.get('search')

		if not search:
			messages.error(request, 'Search value is required')
			return redirect('search_users')

		users = User.objects.filter(
			Q(username__icontains=search) | Q(first_name__icontains=search) |
			Q(last_name__icontains=search)
		).order_by('-date_joined')

		context = {
			'users': users,
			'count': users.count()
		}

	return render(request, 'user/search-users.html', context)
from django.urls import path
from .views import (
	register_user, login_user, forgot_password, 
	reset_password, profile_setting, logout_user,
	profile, search_users
)

urlpatterns = [
	# auth
	path('register/', register_user, name='register_user'),
	path('login/', login_user, name='login_user'),
	path('logout/', logout_user, name='logout_user'),
	path('forgot-password/', forgot_password, name='forgot_password'),
	path('reset-password/<str:reset_id>/', reset_password, name='reset_password'),

	# profile
	path('settings/', profile_setting, name='profile_setting'),
	path('profile/<str:username>/', profile, name='profile'),

	# user
	path('friend/search/', search_users, name='search_users'),
]
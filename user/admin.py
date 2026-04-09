from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
	list_display = ['username', 'email', 'first_name', 'last_name', 'date_joined']
	search_fields = ['username', 'email', 'first_name', 'last_name']
	list_filter = ['is_superuser', 'is_staff', 'date_joined']

admin.site.register(User, UserAdmin)
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from django.conf import settings
import cloudinary.uploader
import cloudinary
from django.utils import timezone
import uuid
from django.core.mail import EmailMessage
from django.urls import reverse

class User(AbstractUser):
	bio = models.TextField(null=True, blank=True)
	profile_image =  CloudinaryField(folder=f'{settings.CLOUDINARY_MEDIA_PREFIX_URL}/profile_images', blank=True, null=True)
	number_of_friends = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.username

	def delete_profile_image(self):
		try:
			cloudinary.uploader.destroy(self.profile_image.public_id)
		except Exception as e:
			pass

	def get_profile_image(self):
		if self.profile_image:
			return self.profile_image.url
		elif self.first_name and self.last_name:
			return f"https://ui-avatars.com/api/?background=667eea&color=fff&rounded=true&size=100&bold=true&name={self.first_name}+{self.last_name}"
		return settings.DEFAULT_USER_PROFILE_IMAGE

	def send_password_reset_email(self, request, password_reset_url, reset_id):

		email = EmailMessage(
			'Reset your password',
			f'Reset your password using the link below:\n\n\n{password_reset_url}',
			settings.EMAIL_HOST_USER,
			[self.email]
		)
		email.fail_silently = True
		email.send()

class PasswordResetCode(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	reset_id = models.UUIDField(default=uuid.uuid4, unique=True,editable=False)
	created_when = models.DateTimeField(auto_now_add=True)

	def has_expired(self):
		return timezone.now() > self.created_when + timezone.timedelta(minutes=10)
    
	def __str__(self):
		return self.reset_id
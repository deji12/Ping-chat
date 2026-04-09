from django.db import models
from user.models import User
from cloudinary.models import CloudinaryField
from django.conf import settings

class Message(models.Model):
	friendship = models.ForeignKey('friend.Friendship', related_name='messages', on_delete=models.CASCADE)
	sent_by = models.ForeignKey(User, on_delete=models.CASCADE)
	text_content = models.TextField(null=True, blank=True)
	image = CloudinaryField(folder=f'{settings.CLOUDINARY_MEDIA_PREFIX_URL}/chat_images', blank=True, null=True)
	is_read = models.BooleanField(default=False)
	sent_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Message from {self.sent_by} in {self.friendship}"

	def image_url(self):
		if self.image:
			return self.image.url
		return ''

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
	reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )

	def __str__(self):
		return f"Message from {self.sent_by} in {self.friendship}"

	def image_url(self):
		if self.image:
			return self.image.url
		return ''

	def reply_to_preview(self):
		"""Returns a short preview of the message being replied to."""
        
		if not self.reply_to:
			return None
		return {
            'sender_name': self.reply_to.sent_by.get_full_name() or self.reply_to.sent_by.username,
            'text': (self.reply_to.text_content or '')[:80],
            'has_image': bool(self.reply_to.image),
            'image_url': self.reply_to.image_url() if self.reply_to.image else None,
            'id': self.reply_to.id,
		}


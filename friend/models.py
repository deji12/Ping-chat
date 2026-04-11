from django.db import models
from user.models import User
from messaging.models import Message


class FriendshipStatus(models.TextChoices):
    pending = 'pending', 'Pending'
    accepted = 'accepted', 'Accepted'
    deleted = 'deleted', 'Deleted'

class Friendship(models.Model):

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'   
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_friend_requests' 
    )
    status = models.CharField(
    	max_length=20, 
    	choices=FriendshipStatus.choices, 
    	default=FriendshipStatus.pending
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_sent_when = models.DateTimeField(auto_now=True)
    friend_request_accept_at = models.DateTimeField(null=True, blank=True)
    number_of_messages_sent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.from_user} → {self.to_user}"


    def get_friend(self, user):
        """Return the other user in this friendship (the friend)."""
        if self.from_user == user:
            return self.to_user
        return self.from_user

    def last_sent_message(self):
        return Message.objects.filter(friendship=self).order_by('-id').first()

    def get_messages(self, user):
        messages = self.messages.all().order_by('sent_at')
        if self.from_user == user:
            messages.filter(sent_by=self.to_user).update(is_read=True)
        else:
            messages.filter(sent_by=self.from_user).update(is_read=True)
        return messages
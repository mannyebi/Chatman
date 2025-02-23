from django.db import models
from users.models import User
# Create your models here.

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="sent_message", null=True)
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="received_messages", null=True)
    # group = models.ForeignKey("Group", on_delete=models.CASCADE, null=True, blank=True)  # For group chats
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="uploads/messsage/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

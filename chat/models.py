from django.db import models
from users.models import User
# Create your models here.

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="sent_message", null=True)
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="received_messages", null=True)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="attachment")
    file = models.FileField(upload_to="uploads/messsage/")

    def __str__(self):
        return f"Attachment for Message ID {self.message.id}"


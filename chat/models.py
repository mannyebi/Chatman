from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
import os

User = get_user_model()

# Create your models here.

class ChatRoom(models.Model):
    """
    Represents a chat room for grouping messages.
    """
    name = models.CharField(max_length=255, unique=True)
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, related_name="chat_rooms")
    bio = models.CharField(max_length=255, null=True, blank=True)
    profile_picuter = models.ImageField(upload_to="chat_pics/", null=True, blank=True)
    http_link = models.URLField(blank=True, null=True)
    is_public = models.BooleanField(default=True)

    @property
    def participant_count(self):
        """return the number of participants in a chat room
        """
        return self.participants.count()

    def __str__(self):
        if self.is_group:
            return f"Public group: {self.name} ({self.participant_count})" if self.is_public else f"Private group: {self.name} ({self.participant_count})"
        return self.name
    
def message_file_path(instance, filename):
    # Example: messages/username/2025/08/filename.ext
    return os.path.join(
        "messages",
        instance.uploader.username,
        datetime.now().strftime("%Y/%m"),
        filename
    )


class File(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_files")
    file = models.FileField(upload_to=message_file_path)
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploader} - {self.filename[:20]}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(null=True, blank=True)
    files = models.ManyToManyField(File, related_name="messages", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        if self.files.count() > 0:
            return f'{self.sender.username} sent {self.files.count()} files'
        return f'{self.sender.username}: {self.text[:20]}'
        
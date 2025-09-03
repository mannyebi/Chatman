from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
import os
from wallet.models import Transaction

User = get_user_model()

# Create your models here.

class ChatRoom(models.Model):
    """
    Represents a chat room for grouping messages.
    """
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, null=True)
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, through="ChatMembership", related_name="chat_rooms")
    bio = models.CharField(max_length=255, null=True, blank=True)
    profile_picuter = models.ImageField(upload_to="chat_pics/", null=True, blank=True)
    http_link = models.URLField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    

    @property
    def participant_count(self):
        """return the number of participants in a chat room
        """
        return self.participants.count()
            
    @property
    def avatar(self):
        return self.chatroom_name()[:1]

    def chatroom_name(self, user=None):
        if not self.is_group and user:
            other_user = self.participants.exclude(id=user.id).first()
            if other_user:
                return f"{other_user.first_name} {other_user.last_name}".strip()
            return "Unknown"
        return self.display_name or "Unknown"
        
    def chatroom_username(self, user):
        if not self.is_group:
            other_user = self.participants.exclude(id=user.id).first()
            if other_user :
                return other_user.username
            return ""

            
    
    def chat_profile_picture(self, user):
        if not self.is_group:
            other_user = self.participants.exclude(id=user.id).first()
            if other_user:
                return other_user.profile_picture.url



    def __str__(self):
        if self.is_group:
            return f"Public group: {self.name} ({self.participant_count})" if self.is_public else f"Private group: {self.name} ({self.participant_count})"
        return f"Priavte chat {self.participants.all()[0].first_name} & {self.participants.all()[1].first_name}"
    
def message_file_path(instance, filename):
    # Example: messages/username/2025/08/filename.ext
    return os.path.join(
        "messages",
        instance.uploader.username,
        datetime.now().strftime("%Y/%m"),
        filename
    )


class ChatMembership(models.Model):
    ROLE_CHOICES = [
        ("owner", "owner"),
        ("admin", "Admin"),
        ("participant", "Participant"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chatroom = models.ForeignKey("ChatRoom", on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, default="participant")

    class Meta:
        unique_together = ("user", "chatroom")

    def __str__(self):
        return f"{self.user.username} in {self.chatroom.name} ({self.role})"


class File(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_files")
    file = models.FileField(upload_to=message_file_path)
    filename = models.CharField(max_length=255, null=True, blank=True)
    content_type = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploader} - {self.filename[:20]}"


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(null=True, blank=True)
    files = models.ManyToManyField(File, related_name="messages", blank=True, null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, related_name="transfer_notifications", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

        indexes = [ #this would help fetching messages based on the room, and timestamps
        models.Index(fields=["room", "timestamp"]),
    ]

    def __str__(self):
        if self.files.count() > 0:
            return f'{self.sender.username} sent {self.files.count()} files'
        return f'{self.sender.username}: {self.text[:20]}'
        
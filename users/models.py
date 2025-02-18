from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
import pyotp
import uuid
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, user_id, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not user_id:
            raise ValueError("User ID is required")
        email = self.normalize_email(email)
        user = self.model(email=email, user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, user_id, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, user_id, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    user_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    secret_key = models.CharField(max_length=32)
    hotp_counter = models.PositiveIntegerField(default=1)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        #generate a user id, if doesn't exist, using their email domain
        if not self.user_id:
            self.user_id = str(uuid.uuid4())[:10]
        if not self.secret_key:
            self.secret_key = pyotp.random_base32()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user_id



class UserBlock(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocker")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')  # Prevent duplicate blocks


    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"
from django.contrib import admin
from .models import Message, ChatRoom, File, ChatMembership
# Register your models here.
admin.site.register(Message)
admin.site.register(ChatRoom)
admin.site.register(File)
admin.site.register(ChatMembership)
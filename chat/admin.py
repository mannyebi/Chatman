from django.contrib import admin
from chat.models import Message, MessageAttachment

# Register your models here.
admin.site.register(Message)
admin.site.register(MessageAttachment)
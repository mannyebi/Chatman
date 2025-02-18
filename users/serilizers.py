from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailSerilizer(serializers.Serializer):
    email = serializers.EmailField()


class OTPVerificationSerilizer(serializers.Serializer):
    otp = serializers.CharField(min_length=4, max_length=6)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

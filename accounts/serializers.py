from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class StarterSignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    bio = serializers.CharField(max_length=500, required=False, allow_blank=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")

        from accounts import services

        if not services.insure_uniqueness(email, username):
            raise serializers.ValidationError("A user with this email or username already exists.")
        return attrs


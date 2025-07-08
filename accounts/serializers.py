from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts import services

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


class ResetPasswordConfirmSerializer(serializers.Serializer):
    uid = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = attrs.get("uid")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        token = services.validate_uid(str(uid))

        if not token:
            raise serializers.ValidationError("Invalid UID.")
        
        if token.is_expired():
            raise serializers.ValidationError("Token has expired.")

        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        attrs["user"] = token.user
        return attrs

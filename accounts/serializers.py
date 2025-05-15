from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.validators import EmailValidator

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles validation of user registration data including password confirmation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        error_messages={
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(
        validators=[EmailValidator()],
        error_messages={
            'invalid': 'Please enter a valid email address.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {
            'username': {'min_length': 3},
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Handles validation of login credentials.
    """
    username = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Username is required.'
        }
    )
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'Password is required.'
        }
    )

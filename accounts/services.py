from typing import Optional
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

def create_user(
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str
) -> User:
    """
    Create a new user with the provided credentials.
    
    Args:
        username: The username for the new user
        email: The email address for the new user
        password: The password for the new user
        first_name: The first name of the user
        last_name: The last name of the user
        
    Returns:
        User: The newly created user object
    """

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    return user

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with the provided credentials.
    
    Args:
        username: The username to authenticate
        password: The password to authenticate
        
    Returns:
        Optional[User]: The authenticated user if successful, None otherwise
    """
    user = authenticate(username=username, password=password)
    if user is None:
        raise ValidationError("Invalid credentials")
    return user



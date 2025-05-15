from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from .serializers import UserRegisterSerializer, UserLoginSerializer
from .services import create_user, authenticate_user
from django.contrib.auth import login, logout

# Create your views here.
class RegisterView(APIView):
    """
    API view for user registration.
    Handles user registration and returns authentication token.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle POST request for user registration.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: JSON response containing user data and authentication token
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name']
            )
            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "status": "success",
                    "message": "User created successfully",
                    "data": {
                        "user": serializer.data,
                        "token": token.key
                    }
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get(self, request):
        """
        Handle GET request for API welcome message.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: JSON response containing welcome message
        """
        return Response(
            {
                "status": "success",
                "message": "Welcome to the Chatman API"
            },
            status=status.HTTP_200_OK
        )


class LoginView(APIView):
    """
    API view for user login.
    Handles user authentication and returns authentication token.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle POST request for user login.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: JSON response containing authentication token
        """
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = authenticate_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response(
                {
                    "status": "success",
                    "message": "Login successful",
                    "data": {"token": token.key}
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )



class TestPageJustForLoggedInUsers(APIView):
    """
    API view for testing authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": f"hi {request.user.username}"}, status=status.HTTP_200_OK)    
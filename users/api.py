from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from .serilizers import EmailSerilizer, OTPVerificationSerilizer, UserLoginSerializer
from .services import services
from .models import User
from django.db import transaction
from .authentication import ApiKeyAuthentication
from rest_framework.authtoken.models import Token
from django_ratelimit.decorators import ratelimit




@api_view(["POST"])
@authentication_classes([ApiKeyAuthentication])
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def send_otp_api(request):
    serializer  = EmailSerilizer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email']
    new_user = services.new_user_checker(email) #user instance will be returned if user is not created, or its created but inactive. else None will be returned

    if not new_user: #check if user is not signed up before. or its inactive
        return Response({"error":"User already exists, please login"}, status=status.HTTP_400_BAD_REQUEST)
    
    hotp_secret = new_user.secret_key
    hotp_counter = new_user.hotp_counter

    hotp_instance = services.generate_hotp_instance(hotp_secret)
    services.send_otp(email, hotp_instance, hotp_counter)

    return Response({"message":"Otp sent to email"}, status=status.HTTP_200_OK)




@api_view(["POST"])
@authentication_classes([ApiKeyAuthentication])
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def validate_otp_api(request, email):
    serializer = OTPVerificationSerilizer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    inputed_otp = serializer.validated_data['otp']
    
    
    with transaction.atomic():
        user = services.get_user_instance(email=email)
        secret = user.secret_key
        counter = user.hotp_counter

        if not counter or not secret or not user:
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if services.verify_otp(secret, counter, inputed_otp):
            services.user_created_flow(request, user=user)
            return Response({"message":"user created successfully"}, status=status.HTTP_201_CREATED)
        



@api_view(["POST"])
@authentication_classes([ApiKeyAuthentication])
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def login_api(request):
    serializer = UserLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = services.authenticate_user(request, email=email, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({"message":"login successfull","token":token.key}, status=status.HTTP_200_OK)
    return Response({"error":"Invalid email or cridentials"}, status=status.HTTP_401_UNAUTHORIZED)

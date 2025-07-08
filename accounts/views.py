from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import services
from . import signup_storage
import logging
from django.db import IntegrityError
from .serializers import StarterSignupSerializer
from django.utils import timezone
from accounts import models





# Create your views here.

logger = logging.getLogger(__name__)
frontend_domain = "https://test.com" #TODO: get this from .env later

class SignUpView(APIView):
    def post(self, request):
        serializer = StarterSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        data = serializer.validated_data
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        bio = data.get("bio", "")
        username = data["username"]
        password = data["password"]
        email = data["email"]

        # generate otp
        try:
            users_secret_base32 = services.generate_random_base32()
            otp = services.generate_otp(users_secret_base32)
            logger.info(f"OTP generated for {email}. otp is : {otp} | secret : {users_secret_base32}")
        except Exception as e:
            logger.error(f"an error occured while generating otp -> {e}")
            return Response({"message":"An error occured"}, status=400)

        #save users data
        try:
            signup_storage.save_signup_data(username=username, password=password, email=email, 
            secret_base32=users_secret_base32, first_name=first_name, last_name=last_name, bio=bio)
        except Exception as e:
            print(f"error -> {e}")
            return Response({"message":"An error occured"}, status=400)

        # send otp email
        try:
            services.send_email(email, "OTP", otp)
            logger.info(f"otp sent to {email} | {otp}")
        except Exception as e:
            logger.error(f"an error occured while sending otp to user -> {e}")
            return Response({"message":"An error occured"}, status=400)
        
        return Response({"message":"an email with verification code sent to your email"}, status=200)


class ValidateUsersOtp(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        email = request.data.get('email')

        #get user's otp using its email
        try:
            user_data = signup_storage.get_signup_data(email) #get the user's data which is stored in previous function
            if user_data is None:
                return Response({"message":"no pending signup with this email"}, status=404)

        except Exception as e:
            logger.error(e)
            return Response({"message":"An error occured while reading sign up data"}, status=400)
    

        #validate otp

        try:
            validation = services.validate_otp(user_data["secret_base32"], otp)
            logger.info(f"validation process for {email} is {validation} | secret : {user_data["secret_base32"]}")
        except Exception as e:
            logger.error(f"error while validating otp -> {e}")
            return Response({"error":"an error occured while validating verfication code"}, status=400)

        if validation:
            try:
                services.create_user(username=user_data["username"], email=email, password=user_data["password"], base32_secret=user_data["secret_base32"],
                                    first_name=user_data["first_name"], last_name=user_data["last_name"], bio=user_data["bio"])
            except IntegrityError as exc:
                return Response({"message":"A user has been created with this email/username"}, status=400)
            except Exception as e:
                logger.error(e)
                return Response({"message":"An error occured while creating user's record "}, status=400)
            return Response({"message": "Account created!"}, status=201)
        else:
            return Response({"error": "Invalid OTP"}, status=400)


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get("email")

        #get user by its email
        try:
            user = services.get_user_by_email(email)
        except Exception as e:
            logger.error(f"an error occured while getting user based on its email -> {e}")
            return Response({"error":"an error occured while reseting password"}, status=400)
        
        #send email if user exists, and return 200 even if it doesn't exists, to prevent user enumeration

        if user:
            expires_at = timezone.now()
            #generate token
            try:
                token = models.PasswordResetToken.objects.create(user=user, expires_at=expires_at)
            except Exception as e:
                logger.error(f"an error occured while creating PasswordResetToken record for {user} -> {e}")
                return Response({"error":"an error occured while generating new reset password link "}, status=400)
            
            reset_link = f"{frontend_domain}/reset-password/{token.uid}"
            #send link via email
            try:
                services.send_email(email=user.email, sub="Rest Password Link", body=token.uid)
            except Exception as e:
                logger.error(f"an error occured while emailing reset link to {user} -> {e} ")
                return Response({"error":"couldn't send email"}, 400)
            
        return Response({"message":"If your email exists, you'll recieve a reset link."})
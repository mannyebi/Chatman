from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import services
from . import signup_storage
import logging
from django.db import IntegrityError


# Create your views here.

logger = logging.getLogger(__name__)

class SignUpView(APIView):
    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        bio = request.data.get("bio")
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email")
        avatar = request.data.get("avatar")

        #insure email or username is unique

        try:
            email_user_uniqueness = services.insure_uniqueness(email, username)            
            if not email_user_uniqueness:
                return Response({"message":"A user has been created with this email/username"}, status=400)
        except Exception as e:
                return Response({"message":"An error occured"}, status=400)


        # generate otp
        try:
            users_secret_base32 = services.generate_random_base32()
            otp = services.generate_otp(users_secret_base32)
        except Exception as e:
            print(f"log -> {e}")
            return Response({"message":"An error occured"}, status=400)

        #save users data
        try:
            signup_storage.save_signup_data(username=username, password=password, email=email, 
            secret_base32=users_secret_base32, first_name=first_name, last_name=last_name, bio=bio, avatar=avatar)
        except Exception as e:
            print(f"error -> {e}")
            return Response({"message":"An error occured"}, status=400)

        # send otp email
        try:
            services.send_email(email, "OTP", otp)
        except Exception as e:
            print(f"error -> {e}")
            return Response({"message":"An error occured"}, status=400)
        
        return Response({"message":"an email with verification code sent to your email"}, status=200)


class ValidateUsersOtp(APIView):
    def post(self, request):
        otp = request.data.get("otp")
        email = request.data.get('email')

        #get user's otp using its email
        try:
            user_data = signup_storage.get_signup_data(email) #get the user's data which is stored in previous function
            if user_data["secret_base32"] is None:
                return Response({"message":"no pending signup with this email"}, status=404)

        except Exception as e:
            logger.error(e)
            return Response({"message":"An error occured"}, status=400)
    

        #validate otp

        try:
            validation = services.validate_otp(user_data["secret_base32"], otp)

            if validation:
                try:
                    services.create_user(username=user_data["username"], email=email, password=user_data["password"], base32_secret=user_data["secret_base32"],
                                        first_name=user_data["first_name"], last_name=user_data["last_name"], bio=user_data["bio"], profile_picture=user_data["avatar"])
                except IntegrityError as exc:
                    return Response({"message":"A user has been created with this email/username"}, status=400)
                except Exception as e:
                    logger.error(e)
                    return Response({"message":"An error occured"}, status=400)
                return Response({"message": "Account created!"}, status=201)
            else:
                print("base32", user_data["secret_base32"])
                print("otp", otp)
                return Response({"error": "Invalid OTP"}, status=400)
        except Exception as e:
            logger.error(e)
            return Response({"message":"An error occured"}, status=400)

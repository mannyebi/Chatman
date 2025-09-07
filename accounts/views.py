from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from . import services
from . import signup_storage
import logging
from django.db import IntegrityError
from .serializers import StarterSignupSerializer, ResetPasswordConfirmSerializer, UpdateAccountSerializer, CompleteSignupSerializer, ResendOtpSerializer
from django.utils import timezone
from accounts import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from chatman.api_schman import api_response


# Create your views here.

logger = logging.getLogger(__name__)
frontend_domain = "https://test.com" #TODO: get this from .env later
User = get_user_model()

class SignUpView(APIView):
    def post(self, request):

        serializer = StarterSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        username = data["username"]
        password = data["password"]
        email = data["email"]
        first_name = data["first_name"]
        last_name = data["last_name"]
        bio = data["bio"]

        # generate otp
        try:
            users_secret_base32 = services.generate_random_base32()
            otp = services.generate_otp(users_secret_base32)
            
        except Exception as e:
            logger.error(f"an error occured while generating otp -> {e}")
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an internal error occured. try again later .")

        #save users data
        try:
            signup_storage.save_signup_data(
            username=username, password=password,
            email=email, secret_base32=users_secret_base32,
            first_name=first_name, last_name=last_name,
            bio=bio
            )
        except Exception as e:
            logger.error(f"an error occured while storing signup data -> {e}")
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an internal error occured while signing you up. try again later.")

        # send otp email
        try:
            
            services.send_email(email, "OTP", otp)
            logger.info(f"otp sent to {email} | {otp}")

        except Exception as e:
            logger.error(f"an error occured while sending otp email to user -> {e}")
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an internal error occured while sending email. try again later.")
        
        return Response({"message":"an email with verification code sent to your email"}, status=200)


class ValidateUsersOtp(APIView):
    def post(self, request):

        serializer = CompleteSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        otp = data["otp"]
        email = data["email"]

        #get user's otp using its email
        try:
            user_data = signup_storage.get_signup_data(email) #get the user's data which is stored in previous function
            if user_data is None:
                return api_response(Status=status.HTTP_401_UNAUTHORIZED, success=False, data={}, message="", error="no pending signup with this email")
            
            secret_base32 = user_data["secret_base32"]
            username = user_data["username"]
            password = user_data["password"]
            first_name = user_data["first_name"]
            last_name = user_data["last_name"]
            bio = user_data["bio"]

        except Exception as e:
            logger.error(e)
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an error occured, try again in 5 minutes")
    

        #validate otp
        try:
            validation = services.validate_otp(secret_base32, otp)
            logger.info(f"validation process for {email} is {validation} | secret : {secret_base32}")
        except Exception as e:
            logger.error(f"error while validating otp -> {e}")
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="error while validating OTP code. try again in 5 minutes")

        if validation:
            try:
                #create both user's record and its related wallet record.
                services.create_user_with_wallet( 
                username=username, email=email, 
                password=password, base32_secret=secret_base32,
                first_name=first_name, last_name=last_name, bio=bio)
            except IntegrityError:
                return api_response(Status=status.HTTP_409_CONFLICT, success=False, data={}, message="", error="this email/username has been used by another user.")
            except Exception as e:
                logger.error(e)
                return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="An error occured while creating user's record")
            return api_response(Status=status.HTTP_201_CREATED, success=True, data={}, message="Account created", error="")
        else:
            return api_response(Status=status.HTTP_401_UNAUTHORIZED, success=False, data={}, message="", error="Invalid OTP")


class ResendOtpEmail(APIView):

    def post(self, request):

        serializer = ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        email = data["email"]

        #get user's otp using its email
        try:
            user_data = signup_storage.get_signup_data(email) #get the user's data which is stored in previous function
            if user_data is None:
                return api_response(Status=status.HTTP_401_UNAUTHORIZED, success=False, data={}, message="", error="no pending signup with this email")
            
            secret_base32 = user_data["secret_base32"]
            first_name = user_data["first_name"]
            last_name = user_data["last_name"]

        except Exception as e:
            logger.error(e)
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an error occured, try again in 5 minutes")

        # generate otp
        try:
            otp = services.generate_otp(secret_base32)
            
        except Exception as e:
            logger.error(f"an error occured while generating otp -> {e}")
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an internal error occured. try again later .")


        # send otp email
        try:
            services.send_email(email, "OTP CODE FROM CHATMAN", f"Hi dear {first_name} {last_name}. here is your OTP Code: {otp}")
            logger.info(f"otp sent to {email} | {otp}")

        except Exception as e:
            logger.error(f"an error occured while sending otp email to user -> {e}")
            return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an internal error occured while sending email. try again later.")
        
        return Response({"message":"another email with verification code sent to your email"}, status=200)


class PasswordResetRequestView(APIView):

    def post(self, request):
        email = request.data.get("email")

        #get user by its email
        try:
            user = services.get_user_by_email(email)
        except Exception as e:
            logger.error(f"an error occured while getting user based on its email -> {e}")
            return api_response(Status=status.HTTP_400_BAD_REQUEST, success=False, data={}, message="", error="an error occured while reseting password, try again later.")
        
        #send email if user exists, and return 200 even if it doesn't exists, to prevent user enumeration

        if user:
            expires_at = timezone.now() + timezone.timedelta(minutes=5)
            #generate token
            try:
                token = models.PasswordResetToken.objects.create(user=user, expires_at=expires_at)
            except Exception as e:
                logger.error(f"an error occured while creating PasswordResetToken record for {user} -> {e}")
                return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="an error occured while generating new reset password link ")
            
            #send link via email
            try:
                services.send_email(email=user.email, sub="Rest Password Link", body=token.uid)
            except Exception as e:
                logger.error(f"an error occured while emailing reset link to {user} -> {e} ")
                return api_response(Status=status.HTTP_500_INTERNAL_SERVER_ERROR, success=False, data={}, message="", error="couldn't send email")
            
        return api_response(Status=status.HTTP_200_OK, success=True, data={}, message="If your email exists, you'll recieve a reset link.", error="")
    

class PasswordResetConfirmView(APIView):

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]        
        new_password = serializer.validated_data["new_password"]

        try:
            user.set_password(new_password)
            user.save()
        except Exception as e:
            logger.error(f"an error occured while saving new password -> {e}")
            return Response({"error":"an error occured while saving password"}, status=400)
        
        try:
            services.delete_uid(serializer.validated_data["uid"])
        except Exception as e: 
            logger.error(f"An error occurred while deleting UID: {e}")

        return Response({"message":"new password set successfuly"}, status=200)


class UpadteAccountView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        user = request.user

        serializer = UpdateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            services.update_account(request.user, serializer.validated_data)
        except Exception as e:
            logger.error(f"an error occured while upadting user's account -> {e}")
            return Response({"error":"an error occured while updating account, please try again"}, status=400)

        user_profile = {
            "first_name" : user.first_name,
            "last_name" : user.last_name,
            "bio" : user.bio,
            "username" : user.username,
            "profile_picture" : user.profile_picture.url
        }

        return Response(user_profile, status=200)



from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token
    
class MyTokenPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie("refresh_token")  # clear cookie
        return response


class LoadProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """return user's profile information.

        username: enter the user's username that you want its profile to fetch in url query.
        """
        username = self.request.query_params.get('username')
        user = get_object_or_404(User, username=username)

        return Response({
        "first_name":user.first_name,
        "last_name":user.last_name,
        "bio":user.bio,
        "username": user.username,
        "profile_picture": user.profile_picture.url,
        }, status=status.HTTP_200_OK)


class SearchUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").lstrip("@")
        if not query:
            return Response({"results":[]})
        
        users = User.objects.filter(username__istartswith=query).exclude(id=request.user.id)[:10]
        results = [
            {
                "id": f"u{u.id}",
                "userName" : u.username,
                "fullName" : f"{u.first_name} {u.last_name}",
                "chatRoomName": f"pv_{max(u.id, request.user.id)}{min(request.user.id,u.id)}",
                "profilePicture" : u.profile_picture.url
            }
            for u in users
        ]
        return Response({"results": results}, status=status.HTTP_200_OK)
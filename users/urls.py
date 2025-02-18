from django.urls import path
from users.views import *
from users.api import *

urlpatterns = [
    path('login', user_login, name="login"),
    path('sign-up', user_signup, name="sign_up"),
    path('send-otp', send_otp, name="send_otp"),
    path('validate_otp', validate_otp, name="validate_otp"),
    #api urls below
    path('api/send-otp', send_otp_api, name="send_otp_api"),
    path('api/validate-otp/<str:email>', validate_otp_api, name="validate_otp_api"),
    path('api/login', login_api, name="login_api"),
]
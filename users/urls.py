from django.urls import path
from users.views import *
from users.api import *

urlpatterns = [
    path('login', UserLogin.as_view(), name="login"),
    path('sign-up', user_signup, name="sign_up"),
    path('send-otp', send_otp, name="send_otp"),
    path('validate_otp', validate_otp, name="validate_otp"),
    path('reset-password', ResetPasword.as_view(), name="reset_password"),
    path('validate-reset-password-otp', ValidateResetPasswordOtp.as_view(), name="validate_rp_otp"),
    path('Change-password', ChangePassword.as_view(), name="change_password"),
    #api urls below
    path('api/send-otp', send_otp_api, name="send_otp_api"),
    path('api/validate-otp/<str:email>', validate_otp_api, name="validate_otp_api"),
    path('api/login', login_api, name="login_api"),
]
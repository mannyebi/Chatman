from django.urls import path
from accounts import views

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("signup-complete/", views.ValidateUsersOtp.as_view(), name="validate-otp"),
    path("password-reset/request/", views.PasswordResetRequestView.as_view(), name="password-reset-requset"),
    path("password-reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("update-account/", views.UpadteAccountView.as_view(), name="password-reset-confirm"),

]

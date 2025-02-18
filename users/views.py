from django.shortcuts import render, redirect, HttpResponse
from .services import services
from django.contrib import messages
from users.models import User
from django.db import transaction
# Create your views here.


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "please enter email and password")

        user = services.authenticate_user(request, email, password)
        
        if user:
            print("Welcome")
        else:
            print("fuck you")
            messages.error(request, "Invalid Email or Password")

    return render(request, "users/login.html")





#---------------------sign up flow----------------------------

def user_signup(request): #1
    return render(request, "users/signup/email.html")


def send_otp(request): #2
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")


        #this error handling is so crucial. if we don't redirect to the "sign_up" url, the `new_user` error handler will redirect it to login page. so don't change it.
        if not email or not password:
            messages.error(request, "please enter email and password")
            return services.htmx_redirect("sign_up")

        new_user = services.new_user_checker(email, password)

        if not new_user:
            messages.error(request, "this user exists, please login")
            return services.htmx_redirect("login")

        
        hotp_secret = new_user.secret_key #get the user's secret key to generate otp
        hotp_counter = new_user.hotp_counter #get the user's counter

        services.create_session(request=request, session_name='hotp_secret', session_data=hotp_secret)# storing sessions, so I wouldn't need to user db query in validate_otp() for getting gotp_secret and hotp_counter.
        services.create_session(request=request, session_name='hotp_counter', session_data=hotp_counter)# storing sessions, so I wouldn't need to user db query in validate_otp() for getting gotp_secret and hotp_counter.

        hotp_instance = services.generate_hotp_instance(hotp_secret)
        services.send_otp(email, hotp_instance, hotp_counter)

        context = {"email":email}
        return render(request, "users/signup/otp.html", context)
    


def validate_otp(request): #3
    if request.method == "POST":

        inputed_otp = request.POST.get("otp")
        email = request.POST.get("email")

        secret = services.get_session(request=request, session_name="hotp_secret")
        counter = services.get_session(request=request, session_name="hotp_counter")

        if not secret or not counter:
            return HttpResponse("a problem occured") #handling the situation that secret or counter or lost for any reason.

        with transaction.atomic():
            
            if services.verify_otp(secret, counter, inputed_otp):
                services.user_created_flow(request, email=email)
                
                return HttpResponse("true")#these will be a redirect function later.
            else:
                return HttpResponse("False")#these will be a redirect function later.
        

#----------------------------------------------------------------
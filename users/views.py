from django.shortcuts import render, redirect, HttpResponse
from .services import services
from django.contrib import messages
from users.models import User
from django.db import transaction
from django.views import View
from users.forms import LoginForm, ResetPasswordForm, ChangePasswordForm
from django.contrib.auth import login
# Create your views here.


class UserLogin(View):
    template_name = "users/login.html"
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {"form":form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = services.authenticate_user(request, email=email, password=password)

            if user:
                login(request, user)
                messages.success(request, "you logged in")
            else:
                messages.error(request, "Invalid Email or Password")
        else:
            messages.error(request, "please fill the fields correctly")
        
        return redirect("login")





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
        try:
            services.send_otp(email, hotp_instance, hotp_counter)
        except:
            messages.error(request, "A problem occured")
            return services.htmx_redirect("sign_up")

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

#reset password flow 

class ResetPasword(View):
    form_class = ResetPasswordForm
    get_template_name = "users/reset_password/password_reset.html"
    post_template_name = "users/reset_password/otp.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.get_template_name, {"form":form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            user = services.get_user_instance(email=email)

            if not user:
                messages.error(request, "No user found with this email")
                return services.htmx_redirect("reset_password")

            secret = user.secret_key
            counter = user.hotp_counter

            if not secret or not counter:
                messages.error(request, "A problem occured")
                return services.htmx_redirect("reset_password")

            hotp_instance = services.generate_hotp_instance(secret)
            try:
                services.send_otp(email, hotp_instance, counter)
            except:
                messages.error(request, "A problem occured")
                return services.htmx_redirect("reset_password")

        else:
            messages.error(request, "please fill the form correctly")
            return services.htmx_redirect("reset_password")
        
        return render(request, self.post_template_name, {"form":form, "email":email}) #email will send as a context, because we post it as a hidden input to validate the otp.


class ValidateResetPasswordOtp(View):
    form_class = ChangePasswordForm
    template = "users/reset_password/change_password.html"

    def get(self, request, *args, **kwargs):
        return redirect("reset_password")

    def post(self, request, *args, **kwargs):
        form = self.form_class
        inputed_otp = request.POST.get('otp')
        email = request.POST.get("email") 
        services.create_session(request, "email", email) #we use this session in `ChangePassword` view for setting the new password for the user.

        if not inputed_otp or not email: #here we insure that we have email and inputed otp
            messages.error(request, "please try again")
    
    
        user = services.get_user_instance(email=email)
        secret_key = user.secret_key
        counter = user.hotp_counter

        hotp = services.generate_hotp_instance(secret_key)

        if hotp.verify(inputed_otp, counter):
            user.hotp_counter += 1
            user.save()
            return render(request, self.template, {"form":form})
        else:
            messages.error(request, "invalid code entered.")



class ChangePassword(View):
    form_class = ChangePasswordForm
    
    def get(self, request, *args, **kwargs):
        return redirect("reset_password")
    

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        email = services.get_session(request, "email")
        user = services.get_user_instance(email=email)

        if form.is_valid():
            password = form.cleaned_data['password']
            password_confirmation = form.cleaned_data['password_confirmation']

            if password == password_confirmation:
                user.set_password(password)
                user.save()
                print('changed')
                services.delete_session(request, "email")
                #return redirect("account")
                return HttpResponse("new password set")
            else:
                print('goh 1')
                messages.error(request, "passwords are not similar")
                return services.htmx_redirect("change_password")
        else:
            messages.error(request, "please fill the form correctly")
            return HttpResponse(status=204)       

#--------------
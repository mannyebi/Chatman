from django.contrib.auth import authenticate
import random
from django.urls import reverse
from django.shortcuts import HttpResponse
import pyotp
from users.models import User




def create_session(request, session_name, session_data):
    """create session
    """
    request.session[session_name] = session_data


def get_session(request, session_name):
    """return a session using its name
    """
    return request.session.get(session_name)


def delete_session(request, session_name):
    """delete a session using its name
    """
    try:
        del request.session[session_name]
        return True
    except:
        return False
    


def send_email(email, text):
    """Send the text to the email
    """
    print(f"email : {email}\nOTP is : {text}")



def authenticate_user(request, email, password):
    """chekc inputed values authentity
    """
    user = User.objects.filter(email=email).first()
    if user and user.is_active:
        return authenticate(request, email=email, password=password)
    return None



def get_user_instance(email):
    """get user by its email
    """
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None

def new_user_checker(email, password=None):
    """return a user instance if user is not created, ot its created but it's inactive. else return None
    """
    try:
        user = User.objects.get(email=email)

        if user.is_active:
            return None
        
        else:
            return user

    except User.DoesNotExist:
        user = User.objects.create(email=email) #create a new user record if the user is not signed up before.
        user.set_password(password)
        user.save()
        return user



def generate_hotp_instance(secret):
    """Generate 4-digit random passwords
    """
    hotp = pyotp.HOTP(secret)
    return hotp


def send_otp(email, hotp, counter):
    """get the otp and send it
    """
    print(counter, "counter -----------------")
    otp = hotp.at(counter)
    send_email(email, otp)



def verify_otp(secret, counter, inputed_otp):
    """check if the stored otp is the same with inputed otp
    """
    hotp = pyotp.HOTP(secret)
    return hotp.verify(inputed_otp, counter)


def user_created_flow(request, email=None, user=None):
    """do the flow that happens after a user created successfully .
    """
    try:
        user = User.objects.get(email=email) if not user else user
    except User.DoesNotExist:
        return False

    user.hotp_counter += 1 #increase the counter for next uses.
    user.is_active = True #change the is_active to true.
    user.save()

    delete_session(request=request, session_name="hotp_secret")# delete the session for safety and resource handling.
    delete_session(request=request, session_name="hotp_counter")# delete the session for safety and resource handling.

    return True




def htmx_redirect(url):
    """redirect user to the url passed
    """
    response = HttpResponse()
    response["HX-Redirect"] = reverse(url)
    return response



def block_user() :
    ...


def is_user_blocked(blocker, blocked):
    """return True if blocker blocked blocked
    """
    return User.objects.filter(blocked=blocked, blocker=blocker).exists()


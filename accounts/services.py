import pyotp
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import logging


User = get_user_model()
logger = logging.getLogger(__name__)


def generate_random_base32():
    """generate random base32 secret keys
    """
    try:
        return pyotp.random_base32()
    except Exception as e:
        print(f"log -> {e}")
        raise


def generate_otp(secret_base32):
    """generate a time otp using user's base32 secret key
    """
    try:
        return pyotp.TOTP(secret_base32).now()
    except Exception as e:
        print(f"log -> {e}")
        raise


def validate_otp(secret_base32, otp):
    """validate user's inputed otp using its base32 secret key 
    """
    try:
        totp = pyotp.TOTP(secret_base32)
        if totp.verify(otp):
            return True
        else:
            print(totp.now(), "true otp") #just to check,TODO: remove later 
            return False
    except Exception as e:
        logger.error(e)
        raise



def insure_uniqueness(email:str, username:str):
    """return True if no user exists with this email and username, otherwise, return False. 
    Warning: this function is not case sensetive
    """
    try:
        return not User.objects.filter(email=email.lower()).exists() and not User.objects.filter(username=username.lower()).exists()
    except Exception as e:
        logger.error(f"error while checking user credential uniqueness -> {e}")



def create_user(username:str,  email:str, password:str | None = None, **extra_fields):
    """create a user record and return it.

    """
    try:
        return User.objects.create_user(username=username, email=email, password=password, **extra_fields)
    except IntegrityError:
        raise
    except Exception as e:
        logger.exception("Unexpected error while creating user %s", username)
        raise


def send_email(email, sub, body):
    print(f"email `{sub}` sent to  {email} : {body}")



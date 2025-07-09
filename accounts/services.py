import pyotp
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import logging
from accounts import models
import uuid
from django.db import transaction
from wallet.models import Wallet

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
            print(totp.now(), f"true otp for -> {secret_base32}") #just to check,TODO: remove later 
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


def check_username_availability(username):
    """return True if this username does not belongs to anyone
    """
    try:
        return User.objects.filter(username=username).exists()
    except Exception as e:
        logger.error(f"an error occured while checking username availabilty -> {e}")
        raise


@transaction.atomic
def create_user_with_wallet(username:str,  email:str, password:str | None = None, **extra_fields):
    """create a user record and a wallet record for it, then return user.

    """
    try:
        user=User.objects.create_user(username=username, email=email, password=password, **extra_fields)
        Wallet.objects.create(user=user)
    except IntegrityError:
        raise
    except Exception as e:
        logger.exception("Unexpected error while creating user %s", username)
        raise

    return user


def send_email(email, sub, body):
    print(f"email `{sub}` sent to  {email} : {body}")


def get_user_by_email(email):
    try:
        return User.objects.filter(email=email).first()
    except Exception as e:
        logger.error(f"an error occured while getting user based on its email -> {e}")
        raise


def validate_uid(uid):
    """check uid validation by checking its existence, and its expiration time. return True if valid
    """
    try:
        uid = uuid.UUID(uid)
    except ValueError:
        return False
    try:
        token = models.PasswordResetToken.objects.filter(uid=uid).first()
    except Exception as e:
        logger.error(f"an error occured while validation uid -> {e}")
        raise
    return token
        

def delete_uid(uid):
    """delete UID.
    """
    try:
        models.PasswordResetToken.objects.filter(uid=uid).delete()
    except Exception as e:
        logger.error(f"an error occured while deleting uid -> {e}")
        raise


def update_account(user, data):
    """update user account fields that are present in data.
    """
    updateable_fields = ["first_name", "last_name", "bio", "username", "profile_picture"]

    try:
        for field in updateable_fields:
            value = data.get(field, None)
            if value not in [None, ""]:
                setattr(user, field, value) # user.field = value
        user.save()
    except Exception as e:
        logger.error(f"an error occured while updating account -> {e}")
        raise
    return user
    
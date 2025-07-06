import shelve
import os
from django.conf import settings
from datetime import datetime

STORAGE_PATH = os.path.join("signup_data")
DEBUG = True #TODO: get this from .env file

def save_signup_data(username, password, email, secret_base32, avatar, first_name=None, last_name=None, bio=None):
    if DEBUG:
        try:
            with shelve.open(STORAGE_PATH) as db:
                db[email] = {
                    "secret_base32" : secret_base32,
                    "created_at" : datetime.now().isoformat(),
                    "username" : username,
                    "password" : password,
                    "first_name" : first_name,
                    "last_name" : last_name,
                    "bio" : bio,
                    "avatar" : avatar
                }
        except Exception as e:
            print(f"log -> {e}")
            raise
    else:
        #TODO: add redis
        ...


def get_signup_data(email):
    if DEBUG:
        try:
            with shelve.open(STORAGE_PATH) as db:
                return db.get(email)
        except Exception as e:
            print(f"log -> {e}")
            raise
    else:
        #TODO: add redis
        ...
    

def delete_signup_data(email):
    if DEBUG:
        try:
            with shelve.open(STORAGE_PATH) as db:
                if email in db:
                    del db[email]
        except Exception as e:
            print(f"log -> {e}")
            raise
    else:
        #TODO: add redis later
        ...
    
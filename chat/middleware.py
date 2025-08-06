from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
import jwt
from urllib.parse import parse_qs

User = get_user_model()



@database_sync_to_async
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user = User.objects.get(id=access_token['user_id']) 
        return user
    except Exception as e:
        print(f"Error getting user from token: {e}")
        user = None


class JwtAuthnMiddleware:
    """authenticate token inside the request and add a 
    user field to scope, if not authenticated, the user scope value will be None.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            query_params = parse_qs(scope["query_string"].decode("utf8"))
            token_list = query_params.get("token", None)
            if token_list and token_list[0]:
                user = await get_user_from_token(token_list[0])
                scope["user"] = user
            else:
                scope["user"] = None
        except Exception as e:
            print(f"error authenticationg user for websocket: {e}")
            scope["user"] = None
        return await self.app(scope, receive, send)

                
def JwtAuthnMiddlewareStack(app):
    return JwtAuthnMiddleware(app)
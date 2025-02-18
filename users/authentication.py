from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in settings.API_KEYS.values():
            print(settings.API_KEYS)
            raise AuthenticationFailed("Invalid API Key")
        return (None, None)
    


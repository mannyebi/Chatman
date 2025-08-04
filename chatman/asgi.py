import os
from django.core.asgi import get_asgi_application

# First, set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatman.settings')

# Then, get the Django ASGI application instance. This initializes the app registry.
django_asgi_app = get_asgi_application()

# Now, it's safe to import app-specific code that relies on the app registry.
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routing import websocket_urlpatterns
from chat.middleware import JWTAuthMiddlewareStack, MyOwnJwtMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": MyOwnJwtMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
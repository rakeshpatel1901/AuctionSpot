import os
from django.urls import path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import joinauction.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE','auction.settings')
print(f"DJANGO_SETTINGS_MODULE: {os.getenv('DJANGO_SETTINGS_MODULE')}")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            #joinauction.routing.ws_patterns,
            joinauction.routing.ws_patterns
        
        )
    ),
})

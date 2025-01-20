import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from detection.routing import websocket_urlpatterns  # Import your routing from routing.py

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'object_detection_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # For HTTP requests
    "websocket": AuthMiddlewareStack(  # For WebSocket requests
        URLRouter(websocket_urlpatterns)  # Use the WebSocket URL patterns from routing.py
    ),
})

# your_app_name/routing.py
from django.urls import re_path
from . import views

websocket_urlpatterns = [
    re_path(r'ws/detect/', views.DetectionConsumer.as_asgi()),  # WebSocket URL pattern
]

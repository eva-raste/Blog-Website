import os
import django

# ✅ Ensure Django is set up before anything else is imported
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BlogWebsite.settings')
django.setup()  # 🔥 This should be added to initialize Django settings properly

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import blog.routing  # Your app's routing file

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Handles regular HTTP traffic
    "websocket": AuthMiddlewareStack(  # Handles WebSocket connections
        URLRouter(
            blog.routing.websocket_urlpatterns  # Your WebSocket URL patterns
        )
    ),
})

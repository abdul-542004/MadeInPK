import os

from django.conf import settings
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MadeInPK.settings')

# Initialize Django ASGI application early to ensure AppRegistry is populated
django_asgi_app = get_asgi_application()

# Import routing and middleware after Django is initialized
from api import routing
from api.middleware import TokenAuthMiddlewareStack

websocket_application = TokenAuthMiddlewareStack(
    URLRouter(
        routing.websocket_urlpatterns
    )
)

# Postman and other non-browser WebSocket clients often omit the Origin header.
# Keep origin validation for non-debug environments, but allow local tooling in debug.
if not settings.DEBUG:
    websocket_application = AllowedHostsOriginValidator(websocket_application)

application = ProtocolTypeRouter({
    "http": ASGIStaticFilesHandler(django_asgi_app),
    "websocket": websocket_application,
})

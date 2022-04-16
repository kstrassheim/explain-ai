"""
ASGI config for testsite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application
django_application = get_asgi_application()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


from api_socket import urls as socket_urls
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp_settings')

application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AuthMiddlewareStack(URLRouter(socket_urls))
})


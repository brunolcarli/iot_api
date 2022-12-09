import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
import django
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iot_api.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.

django.setup()

application = get_default_application()

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     'websocket': django_asgi_app
# })

import os

from channels.routing import ProtocolTypeRouter
from django.conf import settings
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

django_asgi_application = get_asgi_application()

if settings.DEBUG:
    django_asgi_application = ASGIStaticFilesHandler(django_asgi_application)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
    }
)

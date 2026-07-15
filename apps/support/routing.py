from django.urls import path

from apps.support.consumers import ModeratorQueueConsumer, SupportConsumer

websocket_urlpatterns = [
    path(
        "ws/support/moderator/",
        ModeratorQueueConsumer.as_asgi(),
        name="support-moderator-queue",
    ),
    path(
        "ws/support/<int:request_id>/",
        SupportConsumer.as_asgi(),
        name="support-chat",
    ),
]

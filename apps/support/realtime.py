import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)
MODERATOR_CHANNEL_GROUP = "support.moderators"


def _broadcast(group_name, event):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    try:
        async_to_sync(channel_layer.group_send)(group_name, event)
    except Exception:
        logger.exception("Failed to broadcast support event to %s", group_name)


def broadcast_support_request_created(request_id):
    _broadcast(
        MODERATOR_CHANNEL_GROUP,
        {
            "type": "support.request.created",
            "request_id": request_id,
        },
    )


def broadcast_support_request_status(support_request):
    event = {
        "type": "support.request.status_changed",
        "request_id": support_request.pk,
        "status": support_request.status,
    }
    _broadcast(f"support.request.{support_request.pk}", event)
    _broadcast(MODERATOR_CHANNEL_GROUP, event)

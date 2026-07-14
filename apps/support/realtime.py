import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def broadcast_support_request_status(support_request):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    try:
        async_to_sync(channel_layer.group_send)(
            f"support.request.{support_request.pk}",
            {
                "type": "support.request.status_changed",
                "status": support_request.status,
            },
        )
    except Exception:
        logger.exception(
            "Failed to broadcast status for support request %s",
            support_request.pk,
        )

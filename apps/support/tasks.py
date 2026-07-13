import logging

from celery import shared_task
from celery import Task
from django.db.models import F
from django.utils import timezone

from apps.support.models import TelegramNotification
from apps.support.telegram_client import (
    TelegramTemporaryError,
    send_telegram_message,
)

logger = logging.getLogger(__name__)


class TelegramNotificationTask(Task):
    autoretry_for = (TelegramTemporaryError,)
    retry_kwargs = {"max_retries": 2}
    retry_backoff = 5
    retry_backoff_max = 60
    retry_jitter = True
    ignore_result = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if args:
            TelegramNotification.objects.filter(pk=args[0]).exclude(
                status=TelegramNotification.Status.SENT
            ).update(
                status=TelegramNotification.Status.FAILED,
                last_error=str(exc)[:500],
                updated_at=timezone.now(),
            )
        super().on_failure(exc, task_id, args, kwargs, einfo)


def _build_new_request_notification(support_request):
    initial_message = support_request.messages.order_by("created_at", "id").first()
    problem = initial_message.text if initial_message else "—"
    if len(problem) > 300:
        problem = f"{problem[:300].rstrip()}…"

    return (
        f"Новое обращение #{support_request.pk}\n"
        f"Пользователь: {support_request.user.get_username()}\n"
        f"Проблема: {problem}"
    )


@shared_task(base=TelegramNotificationTask)
def send_new_support_request_notification(notification_id):
    try:
        notification = TelegramNotification.objects.select_related("request__user").get(
            pk=notification_id
        )
    except TelegramNotification.DoesNotExist:
        logger.warning(
            "Telegram notification %s does not exist",
            notification_id,
        )
        return

    if notification.status == TelegramNotification.Status.SENT:
        return

    TelegramNotification.objects.filter(pk=notification.pk).update(
        attempts=F("attempts") + 1,
        last_error="",
        updated_at=timezone.now(),
    )
    send_telegram_message(_build_new_request_notification(notification.request))
    TelegramNotification.objects.filter(pk=notification.pk).update(
        status=TelegramNotification.Status.SENT,
        sent_at=timezone.now(),
        last_error="",
        updated_at=timezone.now(),
    )


def enqueue_new_support_request_notification(notification_id):
    try:
        send_new_support_request_notification.delay(notification_id)
    except Exception:
        TelegramNotification.objects.filter(pk=notification_id).update(
            status=TelegramNotification.Status.FAILED,
            last_error="Could not publish task to Celery broker",
            updated_at=timezone.now(),
        )
        logger.exception(
            "Could not enqueue Telegram notification %s",
            notification_id,
        )

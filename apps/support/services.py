from dataclasses import dataclass
from functools import partial

from django.db import transaction
from django.utils import timezone

from apps.support.exceptions import (
    AlreadyRated,
    AuthenticationRequired,
    InvalidMessage,
    InvalidRating,
    MessagesNotAllowed,
    RequestClosed,
    RequestNotClosed,
    RequestNotInProgress,
    SupportAccessDenied,
    SupportRequestNotFound,
)
from apps.support.models import (
    SupportMessage,
    SupportRating,
    SupportRequest,
    TelegramNotification,
)
from apps.support.permissions import is_moderator


@dataclass(frozen=True, slots=True)
class SendMessageResult:
    request: SupportRequest
    message: SupportMessage
    status_changed: bool


def _ensure_authenticated(user):
    if not getattr(user, "is_authenticated", False):
        raise AuthenticationRequired


def _normalize_message_text(text):
    if not isinstance(text, str):
        raise InvalidMessage

    text = text.strip()
    if not text or len(text) > SupportMessage.MAX_TEXT_LENGTH:
        raise InvalidMessage
    return text


def _get_request_for_update(request_id):
    try:
        return (
            SupportRequest.objects.select_for_update()
            .select_related("user")
            .get(pk=request_id)
        )
    except SupportRequest.DoesNotExist as error:
        raise SupportRequestNotFound from error


@transaction.atomic
def create_support_request(user, text):
    from apps.support.tasks import enqueue_new_support_request_notification

    _ensure_authenticated(user)
    text = _normalize_message_text(text)

    support_request = SupportRequest.objects.create(user=user)
    SupportMessage.objects.create(
        request=support_request,
        author=user,
        text=text,
    )
    notification = TelegramNotification.objects.create(request=support_request)
    transaction.on_commit(
        partial(enqueue_new_support_request_notification, notification.pk)
    )
    return support_request


@transaction.atomic
def send_support_message(request_id, author, text):
    _ensure_authenticated(author)
    text = _normalize_message_text(text)

    support_request = _get_request_for_update(request_id)
    moderator = is_moderator(author)
    owner = support_request.user_id == author.pk

    if not owner and not moderator:
        raise SupportAccessDenied
    if support_request.status == SupportRequest.Status.CLOSED:
        raise RequestClosed
    if (
        support_request.status == SupportRequest.Status.WAITING_MODERATOR
        and not moderator
    ):
        raise MessagesNotAllowed

    message = SupportMessage.objects.create(
        request=support_request,
        author=author,
        text=text,
    )

    now = timezone.now()
    status_changed = False
    update_fields = ["updated_at"]
    support_request.updated_at = now

    if support_request.status == SupportRequest.Status.WAITING_MODERATOR:
        support_request.status = SupportRequest.Status.IN_PROGRESS
        support_request.started_at = now
        update_fields.extend(("status", "started_at"))
        status_changed = True

    support_request.save(update_fields=update_fields)
    return SendMessageResult(
        request=support_request,
        message=message,
        status_changed=status_changed,
    )


@transaction.atomic
def close_support_request(request_id, moderator):
    _ensure_authenticated(moderator)
    if not is_moderator(moderator):
        raise SupportAccessDenied

    support_request = _get_request_for_update(request_id)
    if support_request.status == SupportRequest.Status.CLOSED:
        raise RequestClosed
    if support_request.status != SupportRequest.Status.IN_PROGRESS:
        raise RequestNotInProgress

    now = timezone.now()
    support_request.status = SupportRequest.Status.CLOSED
    support_request.closed_at = now
    support_request.closed_by = moderator
    support_request.updated_at = now
    support_request.save(
        update_fields=("status", "closed_at", "closed_by", "updated_at")
    )
    return support_request


@transaction.atomic
def rate_support_request(request_id, user, helped):
    _ensure_authenticated(user)
    if not isinstance(helped, bool):
        raise InvalidRating

    support_request = _get_request_for_update(request_id)
    if support_request.user_id != user.pk:
        raise SupportAccessDenied
    if support_request.status != SupportRequest.Status.CLOSED:
        raise RequestNotClosed
    if SupportRating.objects.filter(request=support_request).exists():
        raise AlreadyRated

    return SupportRating.objects.create(
        request=support_request,
        helped=helped,
    )

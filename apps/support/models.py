from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class SupportRequest(models.Model):
    class Status(models.TextChoices):
        WAITING_MODERATOR = "waiting_moderator", _("Waiting for moderator")
        IN_PROGRESS = "in_progress", _("In progress")
        CLOSED = "closed", _("Closed")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_requests",
        verbose_name=_("User"),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.WAITING_MODERATOR,
        db_index=True,
        verbose_name=_("Status"),
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Started at"),
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Closed at"),
    )
    closed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closed_support_requests",
        verbose_name=_("Closed by"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Support request")
        verbose_name_plural = _("Support requests")
        indexes = [
            models.Index(fields=("user", "status", "-created_at")),
            models.Index(fields=("status", "-created_at")),
        ]

    def __str__(self):
        return f"#{self.pk} — {self.user} — {self.get_status_display()}"


class SupportMessage(models.Model):
    MAX_TEXT_LENGTH = 4000

    request = models.ForeignKey(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Support request"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_messages",
        verbose_name=_("Author"),
    )
    text = models.TextField(
        validators=[MaxLengthValidator(MAX_TEXT_LENGTH)],
        verbose_name=_("Text"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        ordering = ("created_at", "id")
        verbose_name = _("Support message")
        verbose_name_plural = _("Support messages")
        indexes = [
            models.Index(fields=("request", "created_at")),
        ]

    def __str__(self):
        return f"Message #{self.pk} in request #{self.request_id}"


class SupportRating(models.Model):
    request = models.OneToOneField(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="rating",
        verbose_name=_("Support request"),
    )
    helped = models.BooleanField(verbose_name=_("Helped"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        verbose_name = _("Support rating")
        verbose_name_plural = _("Support ratings")

    def __str__(self):
        result = _("Helped") if self.helped else _("Did not help")
        return f"#{self.request_id} — {result}"


class TelegramNotification(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")

    request = models.OneToOneField(
        SupportRequest,
        on_delete=models.CASCADE,
        related_name="telegram_notification",
        verbose_name=_("Support request"),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name=_("Status"),
    )
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name=_("Attempts"))
    last_error = models.TextField(blank=True, verbose_name=_("Last error"))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent at"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Telegram notification")
        verbose_name_plural = _("Telegram notifications")

    def __str__(self):
        return f"#{self.request_id} — {self.get_status_display()}"

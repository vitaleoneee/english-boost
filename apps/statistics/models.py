from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.dictionary.models import Word


class SRSReviewLog(models.Model):
    """An immutable record of one answer submitted to the SRS queue."""

    class ReviewType(models.TextChoices):
        SRS = "SRS", _("SRS review")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="srs_review_logs",
    )
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name="review_logs")
    review_type = models.CharField(
        max_length=32, choices=ReviewType.choices, default=ReviewType.SRS
    )
    user_answer = models.TextField(blank=True)
    correct_answer = models.TextField()
    is_correct = models.BooleanField()
    reviewed_at = models.DateTimeField(auto_now_add=True)
    interval_before = models.PositiveIntegerField()
    interval_after = models.PositiveIntegerField()
    ease_factor_before = models.FloatField()
    ease_factor_after = models.FloatField()
    repetitions_before = models.PositiveIntegerField(default=0)
    repetitions_after = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-reviewed_at"]
        indexes = [
            models.Index(fields=["user", "reviewed_at"]),
            models.Index(fields=["user", "word", "reviewed_at"]),
            models.Index(fields=["user", "is_correct", "reviewed_at"]),
        ]
        verbose_name = _("SRS review log")
        verbose_name_plural = _("SRS review logs")

    def __str__(self):
        return f"{self.user} — {self.word} ({self.reviewed_at:%Y-%m-%d})"

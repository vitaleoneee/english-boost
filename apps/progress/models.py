from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.dictionary.models import Word
from apps.progress.services.modes import LearningMode


class UserWordModeProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="word_mode_progress",
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name="mode_progress",
    )
    mode = models.CharField(
        max_length=20,
        choices=LearningMode.choices,
        verbose_name=_("Learning mode"),
    )
    interval = models.PositiveIntegerField(
        verbose_name=_("Interval in days"),
        default=1,
    )
    repetitions = models.PositiveIntegerField(
        verbose_name=_("Successful repetitions in a row"),
        default=0,
    )
    ease_factor = models.FloatField(
        verbose_name=_("Ease factor"),
        default=2.5,
    )
    next_review_at = models.DateTimeField(
        verbose_name=_("Next review"),
        default=timezone.now,
        null=True,
        blank=True,
    )
    completed = models.BooleanField(default=False, verbose_name=_("Completed"))
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Completed at"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Word mode progress")
        verbose_name_plural = _("Word mode progress records")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "word", "mode"),
                name="unique_user_word_learning_mode",
            )
        ]
        indexes = [
            models.Index(
                fields=("user", "mode", "completed", "next_review_at"),
                name="progress_due_queue_idx",
            )
        ]

    def __str__(self):
        return f"{self.word.english_name} — {self.get_mode_display()}"

    @property
    def is_due(self):
        return (
            not self.completed
            and self.next_review_at is not None
            and self.next_review_at <= timezone.now()
        )


class StudySession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        COMPLETED = "COMPLETED", _("Completed")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )
    mode = models.CharField(
        max_length=20,
        choices=LearningMode.choices,
        verbose_name=_("Learning mode"),
    )
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Status"),
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-started_at",)
        verbose_name = _("Study session")
        verbose_name_plural = _("Study sessions")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "mode"),
                condition=models.Q(status="ACTIVE"),
                name="unique_active_session_per_mode",
            )
        ]

    def __str__(self):
        return f"{self.user} — {self.get_mode_display()}"


class StudySessionCard(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        ANSWERED = "ANSWERED", _("Answered")

    session = models.ForeignKey(
        StudySession,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    progress = models.ForeignKey(
        UserWordModeProgress,
        on_delete=models.CASCADE,
        related_name="session_cards",
    )
    position = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    is_correct = models.BooleanField(null=True, blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("position",)
        verbose_name = _("Study session card")
        verbose_name_plural = _("Study session cards")
        constraints = [
            models.UniqueConstraint(
                fields=("session", "progress"),
                name="unique_progress_per_session",
            ),
            models.UniqueConstraint(
                fields=("session", "position"),
                name="unique_position_per_session",
            ),
        ]

    def __str__(self):
        return f"{self.session} — {self.position}"


class Achievement(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"))
    is_secret = models.BooleanField(default=False, verbose_name=_("Secret achievement"))
    icon = models.CharField(
        max_length=50,
        default="bi-award-fill",
        verbose_name=_("Icon"),
        help_text=_("Bootstrap Icons class, for example: bi-book-fill"),
    )

    class Meta:
        verbose_name = _("Achievement")
        verbose_name_plural = _("Achievements")

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    achievement = models.ForeignKey(
        Achievement, on_delete=models.CASCADE, verbose_name=_("Achievement")
    )
    awarded_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Award date and time")
    )
    is_seen = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("User achievement")
        verbose_name_plural = _("User achievements")
        ordering = ["user", "achievement"]
        constraints = [
            models.UniqueConstraint(
                fields=("user", "achievement"), name="unique_user_achievement"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.achievement.name}"

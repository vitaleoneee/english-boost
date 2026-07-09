import math
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModel

from apps.dictionary.models import Word
from .constants import SRS_LEARNED_THRESHOLD


class UserSRS(LifecycleModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="srs_items",
    )
    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name="srs",
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
    access_timer = models.DateTimeField(
        verbose_name=_("Next review"),
        default=timezone.now,
    )

    class Meta:
        unique_together = ("user", "word")
        verbose_name = _("SRS object")
        verbose_name_plural = _("SRS objects")

    def __str__(self):
        return self.word.english_name

    @property
    def is_due(self):
        return self.access_timer <= timezone.now()

    @property
    def seconds_until_due(self):
        diff = self.access_timer - timezone.now()
        return max(0, int(diff.total_seconds()))

    def update_after_answer(self, correct: int) -> bool:
        """
        SM-2 algorithm.

        Returns True if the word is considered learned.
        """
        now = timezone.now()

        if not correct:
            self.repetitions = 0
            self.interval = 1
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
            self.access_timer = now
        else:
            # Success - calculating the new interval based on SM-2
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = math.ceil(self.interval * self.ease_factor)

            self.repetitions += 1
            self.ease_factor = min(3.0, self.ease_factor + 0.1)
            self.access_timer = now + timedelta(days=self.interval)

        learned = self.interval >= SRS_LEARNED_THRESHOLD

        if learned:
            self.word.status = "LEARNED"
            self.word.save(update_fields=["status"])
            self.save()
            self.delete()
            return True

        self.save()
        return False


class Achievement(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"))
    is_secret = models.BooleanField(default=False, verbose_name=_("Secret achievement"))

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

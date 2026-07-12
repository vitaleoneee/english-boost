from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook

from apps.dictionary.choices import (
    LanguageLevel,
    PartOfSpeech,
    StudyStatus,
    UsageRegister,
)


class Topic(models.Model):
    code = models.SlugField(max_length=100, unique=True, verbose_name=_("Code"))
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    is_system = models.BooleanField(default=True, verbose_name=_("System topic"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")
        ordering = ["name"]
        indexes = [models.Index(fields=["created_at", "updated_at"])]

    def __str__(self):
        return self.name


class Word(LifecycleModel):
    topics = models.ManyToManyField(
        Topic, blank=True, related_name="words", verbose_name=_("Topics")
    )
    english_name = models.CharField(max_length=100, verbose_name=_("English word"))
    russian_name = models.CharField(max_length=100, verbose_name=_("Russian word"))
    part_of_speech = models.CharField(
        choices=PartOfSpeech.choices,
        max_length=20,
        blank=True,
        verbose_name=_("Part of speech"),
    )
    level = models.CharField(
        choices=LanguageLevel.choices,
        max_length=2,
        blank=True,
        verbose_name=_("Language level"),
    )
    register = models.CharField(
        choices=UsageRegister.choices,
        max_length=20,
        blank=True,
        verbose_name=_("Usage register"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        choices=StudyStatus.choices,
        max_length=20,
        verbose_name=_("Status"),
        default=StudyStatus.PROCESS,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="words",
    )

    class Meta:
        verbose_name = _("Word")
        verbose_name_plural = _("Words")
        ordering = ["-status", "english_name"]
        indexes = [models.Index(fields=["created_at", "updated_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "english_name", "russian_name"],
                name="unique_user_word_translation",
            )
        ]

    def __str__(self):
        return self.english_name

    @hook(AFTER_CREATE)
    def on_word_created(self):
        from apps.progress.achievements import AchievementChecker

        checker = AchievementChecker(self.user)
        checker.check_word_count()

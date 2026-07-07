from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_CREATE, LifecycleModel, hook


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["id"]
        indexes = [
            models.Index(fields=["created_at", "updated_at"])
        ]

    def __str__(self):
        return self.name


class Word(LifecycleModel):
    class StudyStatus(models.TextChoices):
        LEARNED = ("LEARNED", _("Learned"))
        PROCESS = ("PROCESS", _("In progress"))

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name=_("Category")
    )
    english_name = models.CharField(max_length=100, verbose_name=_("English word"))
    russian_name = models.CharField(max_length=100, verbose_name=_("Russian word"))
    slug = models.SlugField(
        max_length=100, unique=True, verbose_name=_("Slug"), blank=True, null=True
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
        indexes = [
            models.Index(fields=["created_at", "updated_at"])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "english_name"], name="unique_user_english_word"
            )
        ]

    def __str__(self):
        return self.english_name

    def save(self, *args, **kwargs):
        # TODO: check same slugs
        """
        Method that automatically creates a slug based on english_name when saving a model
        """
        if not self.slug:
            self.slug = slugify(self.english_name)
        super().save(*args, **kwargs)

    @hook(AFTER_CREATE)
    def on_word_created(self):
        from apps.progress.achievements import AchievementChecker

        checker = AchievementChecker(self.user)
        checker.check_word_count()

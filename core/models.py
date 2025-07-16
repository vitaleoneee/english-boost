from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']
        indexes = [
            models.Index(
                fields=['created_at', 'updated_at'],
            )
        ]

    def __str__(self):
        return self.name


class Word(models.Model):
    # Word Study Status Class
    class StudyStatus(models.TextChoices):
        LEARNED = ('LEARNED', 'Изучено')
        PROCESS = ('PROCESS', 'Изучается')

    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    english_name = models.CharField(max_length=100, verbose_name='Слово на английском')
    russian_name = models.CharField(max_length=100, verbose_name='Слово на русском')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=StudyStatus.choices, max_length=20, verbose_name='Статус',
                              default=StudyStatus.PROCESS)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь',
                             related_name='words')

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'
        ordering = ['-status', 'english_name']
        indexes = [
            models.Index(
                fields=['created_at', 'updated_at'],
            )
        ]
        constraints = [
            models.UniqueConstraint(fields=['user', 'english_name'], name='unique_user_english_word')
        ]

    def __str__(self):
        return self.english_name

    def save(self, *args, **kwargs):
        """
        Method that automatically creates a slug based on english_name when saving a model
        """
        if not self.slug:
            self.slug = slugify(self.english_name)
        super().save(*args, **kwargs)

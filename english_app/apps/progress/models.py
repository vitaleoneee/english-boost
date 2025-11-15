from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from english_app.apps.core.models import Word
from .constants import SRS_LEARNED_THRESHOLD, WORD_STATUS_LEARNED


class UserSRS(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='srs_items')
    word = models.OneToOneField(Word, on_delete=models.CASCADE, related_name='srs')
    interval = models.IntegerField(verbose_name='SRS интервал в днях', default=1)
    access_timer = models.DateTimeField(verbose_name='Время доступа к повторению', default=timezone.now)

    class Meta:
        verbose_name = 'SRS объект'
        verbose_name_plural = 'SRS объекты'
        ordering = ['-interval']

    def __str__(self):
        return self.word.english_name

    def get_access_delay(self):
        now = timezone.now()
        if self.access_timer and self.access_timer > now:
            diff = self.access_timer - now
        else:
            diff = timedelta(seconds=0)

        total_seconds = max(0, int(diff.total_seconds()))

        if total_seconds > 0:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            access_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            access_time_str = None

        return total_seconds, access_time_str

    def update_after_answer(self, failure=False):
        now = timezone.now()
        if failure:
            self.interval = 1
            self.access_timer = now
        else:
            self.interval *= 2
            self.access_timer = now + timedelta(days=self.interval)

        if self.interval >= SRS_LEARNED_THRESHOLD:
            self.word.status = WORD_STATUS_LEARNED
            self.word.save()
            self.delete()

        self.save()


class Achievement(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    secret = models.BooleanField(default=False, verbose_name='Секретность достижения')

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering = ['pk']

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name='Достижение')
    awarded_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время получения')

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователя'
        ordering = ['user', 'achievement']
        constraints = [
            models.UniqueConstraint(fields=('user', 'achievement'), name='unique_user_achievement')
        ]

    def __str__(self):
        return f'Достижение пользователя {self.user} - {self.achievement.name}'

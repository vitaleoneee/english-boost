from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.progress.models import (
    Achievement,
    StudySession,
    StudySessionCard,
    UserAchievement,
    UserWordModeProgress,
)


@admin.register(UserWordModeProgress)
class UserWordModeProgressAdmin(ModelAdmin):
    search_fields = ("user__username", "word__english_name")
    list_filter = ("mode", "completed", "interval")
    list_display = (
        "user",
        "word",
        "mode",
        "interval",
        "next_review_at",
        "completed",
    )


@admin.register(StudySession)
class StudySessionAdmin(ModelAdmin):
    search_fields = ("user__username",)
    list_filter = ("mode", "status")
    list_display = ("user", "mode", "status", "started_at", "finished_at")


@admin.register(StudySessionCard)
class StudySessionCardAdmin(ModelAdmin):
    list_filter = ("status", "is_correct")
    list_display = ("session", "position", "progress", "status", "is_correct")


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    search_fields = ("name", "description")
    list_filter = ("is_secret",)
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("id", "name", "icon", "is_secret", "description")


@admin.register(UserAchievement)
class UserAchievementAdmin(ModelAdmin):
    search_fields = ("user__username", "achievement__name")
    list_filter = ("achievement",)
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("user", "achievement", "awarded_at")

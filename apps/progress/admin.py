from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.dictionary.models import Word
from apps.progress.models import UserSRS, Achievement, UserAchievement


@admin.register(UserSRS)
class UserSRSAdmin(ModelAdmin):
    search_fields = ("user__username", "word__english_name")
    list_filter = ("interval",)
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("user", "word", "interval", "access_timer")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "word":
            kwargs["queryset"] = Word.objects.filter(status="PROCESS")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    search_fields = ("name", "description")
    list_filter = ("is_secret",)
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("id", "name", "is_secret", "description")


@admin.register(UserAchievement)
class UserAchievementAdmin(ModelAdmin):
    search_fields = ("user__username", "achievement__name")
    list_filter = ("achievement",)
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("user", "achievement", "awarded_at")

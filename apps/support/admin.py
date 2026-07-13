from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.support.models import (
    SupportMessage,
    SupportRating,
    SupportRequest,
    TelegramNotification,
)


@admin.register(SupportRequest)
class SupportRequestAdmin(ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "created_at",
        "started_at",
        "closed_at",
        "closed_by",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "closed_by")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SupportMessage)
class SupportMessageAdmin(ModelAdmin):
    list_display = ("id", "request", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text", "author__username", "request__user__username")
    autocomplete_fields = ("request", "author")
    readonly_fields = ("created_at",)


@admin.register(SupportRating)
class SupportRatingAdmin(ModelAdmin):
    list_display = ("id", "request", "helped", "created_at")
    list_filter = ("helped", "created_at")
    autocomplete_fields = ("request",)
    readonly_fields = ("created_at",)


@admin.register(TelegramNotification)
class TelegramNotificationAdmin(ModelAdmin):
    list_display = ("id", "request", "status", "attempts", "sent_at", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("request__user__username", "request__user__email")
    autocomplete_fields = ("request",)
    readonly_fields = (
        "request",
        "status",
        "attempts",
        "last_error",
        "sent_at",
        "created_at",
        "updated_at",
    )

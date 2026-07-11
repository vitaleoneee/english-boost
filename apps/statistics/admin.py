from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.statistics.models import SRSReviewLog


@admin.register(SRSReviewLog)
class SRSReviewLogAdmin(ModelAdmin):
    list_display = ("user", "word", "review_type", "is_correct", "reviewed_at")
    list_filter = ("review_type", "is_correct")
    search_fields = ("user__username", "word__english_name", "user_answer")
    readonly_fields = (
        "user",
        "word",
        "review_type",
        "user_answer",
        "correct_answer",
        "is_correct",
        "reviewed_at",
        "interval_before",
        "interval_after",
        "ease_factor_before",
        "ease_factor_after",
        "repetitions_before",
        "repetitions_after",
    )

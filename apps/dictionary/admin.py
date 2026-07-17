from django.contrib import admin
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.urls import path
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

from apps.dictionary.choices import StudyStatus
from apps.dictionary.models import Topic, Word
from apps.progress.services.session_service import create_progress_for_word


@admin.register(Topic)
class TopicAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("id", "code", "name", "is_active", "is_system", "word_count")
    list_filter = ("is_active", "is_system")
    search_fields = ("code", "name")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description=_("Words"))
    def word_count(self, obj):
        return obj.words.count()


@admin.register(Word)
class WordAdmin(ModelAdmin):
    list_display = (
        "user",
        "english_name",
        "display_topics",
        "part_of_speech",
        "level",
        "status",
        "id",
    )
    list_filter = ("status", "part_of_speech", "level", "register", "topics")
    filter_horizontal = ("topics",)
    change_list_template = "admin/dictionary/word/change_list.html"

    @admin.display(description=_("Topics"))
    def display_topics(self, obj):
        return ", ".join(obj.topics.values_list("name", flat=True)) or "—"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            create_progress_for_word(obj)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "generate-test-words/",
                self.admin_site.admin_view(self.generate_test_words),
                name="dictionary_word_generate_test_words",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["generate_test_words_url"] = reverse(
            "admin:dictionary_word_generate_test_words"
        )
        return super().changelist_view(request, extra_context=extra_context)

    def generate_test_words(self, request):
        topic = Topic.objects.get_or_create(
            code="test-words",
            defaults={
                "name": _("Test words"),
                "description": _("Words generated from the admin panel."),
                "is_system": False,
            },
        )[0]
        suffix = timezone.now().strftime("%Y%m%d%H%M%S")
        created_count = 0

        for number in range(1, 11):
            word = Word(
                user=request.user,
                english_name=f"test-word-{suffix}-{number}",
                russian_name=f"тестовое слово {number}",
                status=StudyStatus.PROCESS,
            )
            word.save()
            word.topics.add(topic)
            create_progress_for_word(word)
            created_count += 1

        messages.success(
            request,
            _("Created test words: %(count)s") % {"count": created_count},
        )
        return redirect("admin:dictionary_word_changelist")

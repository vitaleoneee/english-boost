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

from apps.dictionary.models import Category, Word
from apps.progress.models import UserSRS


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("id", "name")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(Word)
class WordAdmin(ModelAdmin):
    list_display = ("user", "english_name", "status", "id")
    change_list_template = "admin/dictionary/word/change_list.html"

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
        category = Category.objects.get_or_create(
            name=_("Test words"),
            defaults={"description": _("Words generated from the admin panel.")},
        )[0]
        suffix = timezone.now().strftime("%Y%m%d%H%M%S")
        created_count = 0

        for number in range(1, 11):
            word = Word(
                user=request.user,
                category=category,
                english_name=f"test-word-{suffix}-{number}",
                russian_name=f"тестовое слово {number}",
                status=Word.StudyStatus.PROCESS,
            )
            word.save()
            UserSRS.objects.get_or_create(user=request.user, word=word)
            created_count += 1

        messages.success(
            request,
            _("Created test words: %(count)s") % {"count": created_count},
        )
        return redirect("admin:dictionary_word_changelist")

from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

from apps.dictionary.models import Category, Word


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
    list_display = ("user", "english_name", "slug", "status", "id")

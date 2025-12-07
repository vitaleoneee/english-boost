from english_app.apps.core.models import Category, Word

from django.db import models
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

admin.site.unregister(User)
admin.site.unregister(Group)


# Admin View of User Model in Django Unfold
@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("id", "username", "email", "is_staff")


# Admin View Group Model from Django Unfold
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)
    filter_horizontal = ()
    fields = ("name",)


# Registering the Category application in the admin panel
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("id", "name")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


# Registering the Word application in the admin panel
@admin.register(Word)
class WordAdmin(ModelAdmin):
    list_display = ("user", "english_name", "slug", "status", "id")

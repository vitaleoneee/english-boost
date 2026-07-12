from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.dictionary.models import Topic, Word


class NewDictionaryWordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["topics"].queryset = Topic.objects.filter(is_active=True)
        for field in self.fields.values():
            if field.required:
                field.label = format_html(
                    '{} <span class="new-word-required-badge">{}</span>',
                    field.label,
                    _("Required"),
                )

    class Meta:
        model = Word
        fields = [
            "english_name",
            "russian_name",
            "topics",
            "part_of_speech",
            "level",
            "register",
            "status",
        ]
        widgets = {
            "topics": forms.CheckboxSelectMultiple(),
        }

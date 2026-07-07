from django import forms

from apps.dictionary.models import Word


class NewDictionaryWordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ["category", "english_name", "russian_name", "status"]

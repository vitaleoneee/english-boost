from django import forms
from django.utils.translation import gettext_lazy as _


class WordCheckForm(forms.Form):
    translate_input = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Enter translation")}
        )
    )

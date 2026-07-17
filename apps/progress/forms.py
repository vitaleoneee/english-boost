from django import forms
from django.utils.translation import gettext_lazy as _


class AnswerForm(forms.Form):
    answer = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": _("Type your answer"),
                "autocomplete": "off",
                "autofocus": True,
            }
        ),
    )

from django import forms
from django.utils.translation import gettext_lazy as _


# Feedback form for collecting data from user to developer
class ContactForm(forms.Form):
    full_name = forms.CharField(
        label=_("Full name"),
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "id": "name",
            }
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "id": "email",
            }
        ),
    )
    message = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(
            attrs={"class": "form-control", "id": "message", "style": "height: 150px"}
        ),
    )

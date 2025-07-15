from django import forms


class WordCheckForm(forms.Form):
    translate_input = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Введите перевод'}))

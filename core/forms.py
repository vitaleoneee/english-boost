from django import forms

from core.models import Word


# Ajax feedback form for collecting data from user to developer
class ContactForm(forms.Form):
    full_name = forms.CharField(label='Полное имя',
                                max_length=100,
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'id': 'name', }))
    email = forms.EmailField(label='Email',
                             widget=forms.EmailInput(attrs={'class': 'form-control',
                                                            'id': 'email', }))
    message = forms.CharField(label='Сообщение',
                              widget=forms.Textarea(attrs={'class': 'form-control',
                                                           'id': 'message',
                                                           'style': 'height: 150px'}))


# Form for adding a new word to the user's dictionary
class NewDictionaryWordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['category', 'english_name', 'russian_name', 'status']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control', }),
            'english_name': forms.TextInput(attrs={'class': 'form-control', }),
            'russian_name': forms.TextInput(attrs={'class': 'form-control', }),
            'status': forms.Select(choices=Word.StudyStatus.choices, attrs={'class': 'form-control', }),
        }

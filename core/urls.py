from django.urls import path
from core.views import index, ajax_contact, dictionary, new_dictionary_word, delete_selected_words

app_name = 'core'

urlpatterns = [
    # Ajax form processing route
    path('ajax-send/', ajax_contact, name='ajax-send'),
    # Home page route
    path('', index, name='index'),
    # Dictionary page route
    path('dictionary/', dictionary, name='dictionary'),
    # Route to add a new word to the dictionary
    path('new-dictionary-word/', new_dictionary_word, name='new-dictionary-word'),
    # Route to remove a word from a dictionary
    path('dictionary/delete/', delete_selected_words, name='delete_selected_words'),
]

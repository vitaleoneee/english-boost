from django.urls import path
from english_app.apps.core.views import (
    DictionaryListView,
    index,
    new_dictionary_word,
    delete_selected_words,
    send_features,
)

app_name = "core"

urlpatterns = [
    # Ajax form processing route (HTMX)
    path("send-features/", send_features, name="send-features"),
    # Home page route
    path("", index, name="index"),
    # Dictionary page route
    path("dictionary/", DictionaryListView.as_view(), name="dictionary"),
    # Route to add a new word to the dictionary
    path("new-dictionary-word/", new_dictionary_word, name="new-dictionary-word"),
    # Route to remove a word from a dictionary
    path("dictionary/delete/", delete_selected_words, name="delete_selected_words"),
]

from django.urls import path

from apps.dictionary.views import (
    delete_selected_words,
    DictionaryListView,
    NewDictionaryWordView,
)

app_name = "dictionary"

urlpatterns = [
    path("dictionary/", DictionaryListView.as_view(), name="dictionary-list"),
    path("new-dictionary-word/", NewDictionaryWordView.as_view(), name="new-dictionary-word"),
    path("dictionary/delete/", delete_selected_words, name="delete-selected-words")
]

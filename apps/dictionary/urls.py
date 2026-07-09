from django.urls import path

from apps.dictionary.views import (
    delete_selected_words,
    DictionaryListView,
    NewDictionaryWordView,
    search_words,
)

app_name = "dictionary"

urlpatterns = [
    path("", DictionaryListView.as_view(), name="dictionary-list"),
    path(
        "new-dictionary-word/",
        NewDictionaryWordView.as_view(),
        name="new-dictionary-word",
    ),
    path("delete/", delete_selected_words, name="delete-selected-words"),
    path("search/", search_words, name="search-words"),
]

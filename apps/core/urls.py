from django.urls import path

from apps.core.views import (
    DictionaryListView,
    IndexView,
    new_dictionary_word,
    delete_selected_words,
    send_features,
)

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("dictionary/", DictionaryListView.as_view(), name="dictionary"),
    path("new-dictionary-word/", new_dictionary_word, name="new-dictionary-word"),
    path("dictionary/delete/", delete_selected_words, name="delete_selected_words"),

    # HTMX form processing route
    path("send-features/", send_features, name="send-features"),
]

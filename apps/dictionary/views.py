from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django_htmx.http import trigger_client_event
from django_tables2 import SingleTableView

from apps.dictionary.forms import NewDictionaryWordForm
from apps.dictionary.models import Word
from apps.dictionary.tables.dictionary import DictionaryTable
from apps.progress.achievements import AchievementChecker
from apps.progress.models import UserSRS
from redis_service import r


class DictionaryListView(LoginRequiredMixin, SingleTableView):
    model = Word
    context_object_name = "words"
    template_name = "dictionary/dictionary_list.html"
    table_class = DictionaryTable
    context_table_name = "dictionary_table"

    # TODO : Add pagination here
    # TODO : Improve table display

    def get_queryset(self):
        # Filter words by the current user
        return Word.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "selected": "dictionary",
                "words": self.get_queryset(),
            }
        )
        return context


class NewDictionaryWordView(LoginRequiredMixin, CreateView):
    form_class = NewDictionaryWordForm
    template_name = "dictionary/new_dictionary_word.html"
    success_url = reverse_lazy("dictionary:dictionary-list")

    def form_valid(self, form):
        word = form.save(commit=False)
        word.user = self.request.user

        try:
            word.save()
        except IntegrityError:
            messages.error(
                self.request,
                _("A word with this English and Russian translation already exists."),
            )
            return self.form_invalid(form)

        if word.status == Word.StudyStatus.PROCESS:
            UserSRS.objects.create(word=word, user=self.request.user)
        messages.info(self.request, _("Added a new word"))

        return redirect(self.success_url)


@login_required
@require_POST
def delete_selected_words(request):
    if not request.htmx:
        return redirect("dictionary:dictionary-list")

    ids = request.POST.getlist("selected_words")

    if ids:
        qs = Word.objects.filter(user=request.user, pk__in=ids)
        deleted_count = qs.count()
        qs.delete()

        if deleted_count:
            r.incrby(
                f"{request.user.username}:{request.user.id}:del_counter",
                deleted_count,
            )

            # 07.07.2026
            # This behavior is not implemented via a hook
            # because `qs.delete()` (a bulk update) is executed,
            # rather than the deletion of an individual instance
            checker = AchievementChecker(request.user)
            checker.check_deleted_words()

        messages.info(
            request,
            _("Deleted words: %(count)s") % {"count": deleted_count},
        )
    else:
        messages.error(request, _("You have not selected any words."))

    words = Word.objects.filter(user=request.user)
    context = {
        "words": words,
        "dictionary_table": DictionaryTable(words),
    }
    response = render(request, "dictionary/partials/dictionary_table.html", context)
    trigger_client_event(response, "wordDeleted")
    return response

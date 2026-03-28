import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from english_app.apps.core.tables.dictionary import DictionaryTable
from english_app.apps.progress.models import UserSRS
from redis_service import r

from english_app.apps.core.forms import ContactForm, NewDictionaryWordForm
from english_app.apps.core.models import Word
from english_app.apps.core.utils import check_and_set_achievements

from django_tables2 import SingleTableView


def index(request):
    """
    Main Page Controller with Ajax Form Output
    """
    form = ContactForm()
    return render(request, "core/index.html", {"selected": "index", "form": form})


class DictionaryListView(LoginRequiredMixin, SingleTableView):
    model = Word
    context_object_name = "words"
    template_name = "core/dictionary.html"
    table_class = DictionaryTable
    context_table_name = "dictionary_table"

    # TODO : Add pagination here

    def get_queryset(self):
        # Filter words by the current user
        return Word.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # Set achievements and pop messages from session
        check_and_set_achievements(self.request, "check_word_count")
        achievement_message = self.request.session.pop("achievement_message", None)
        default_message = self.request.session.pop("default_message", None)
        context.update(
            {
                "selected": "dictionary",
                "words": self.get_queryset(),
                "achievement_message": achievement_message,
                "default_message": default_message,
            }
        )
        return context


@login_required
def new_dictionary_word(request):
    """
    Page controller with a form for adding a word to the dictionary
    """
    form = NewDictionaryWordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        word = form.save(commit=False)
        word.user = request.user
        word.save()
        # Automatically create SRS model when adding a new word to the dictionary
        UserSRS.objects.create(word=word, user=request.user)
        return redirect("core:dictionary")
    return render(request, "core/new_dictionary_word.html", {"form": form})


@require_POST
def send_features(request):
    """
    Ajax form implementation controller using HTMX
    """
    form = ContactForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            "core/partials/send_form_btn.html",
            {"message": f"Форма не может быть отправлена. Повторите позже"},  # noqa: F541
        )

    full_name = form.cleaned_data["full_name"]
    email = form.cleaned_data["email"]
    message = form.cleaned_data["message"]
    from_email = f"{full_name} <{email}>"
    # Sending a message to the developer using backend smtp
    try:
        send_mail(
            subject=f"Сообщение от {full_name} ({email})!",
            message=message,
            from_email=from_email,
            recipient_list=[os.environ.get("EMAIL_HOST_USER")],
        )
        return render(
            request,
            "core/partials/send_form_btn.html",
            {"message": "Форма успешно отправлена!"},  # noqa: F841
        )
    except Exception as e:  # noqa: F841
        return render(
            request,
            "core/partials/send_form_btn.html",
            {"message": f"Форма не может быть отправлена. Повторите позже"},  # noqa: F541
        )


@require_POST
@login_required
def delete_selected_words(request):
    ids = request.POST.getlist("selected_words")
    if ids:
        Word.objects.filter(pk__in=ids, user=request.user).delete()
        r.incrby(f"{request.user.username}:{request.user.id}:del_counter", len(ids))
        check_and_set_achievements(request, "check_deleted_words")
        request.session["default_message"] = len(ids)
    else:
        request.session["default_message"] = "Вы не выбрали ни одного слова"
    return redirect("core:dictionary")

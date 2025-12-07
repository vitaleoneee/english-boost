import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from english_app.apps.progress.models import UserSRS
from redis_service import r

from english_app.apps.core.forms import ContactForm, NewDictionaryWordForm
from english_app.apps.core.models import Word
from english_app.apps.core.utils import check_and_set_achievements


def index(request):
    """
    Main Page Controller with Ajax Form Output
    """
    form = ContactForm()
    return render(request, "core/index.html", {"selected": "index", "form": form})


@login_required
def dictionary(request):
    """
    Page controller with dictionary output
    """
    words = Word.objects.filter(user=request.user)
    check_and_set_achievements(request, "check_word_count")
    achievement_message = request.session.pop("achievement_message", None)
    default_message = request.session.pop("default_message", None)
    return render(
        request,
        "core/dictionary.html",
        {
            "selected": "dictionary",
            "words": words,
            "achievement_message": achievement_message,
            "default_message": default_message,
        },
    )


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
def ajax_contact(request):
    """
    Ajax form implementation controller
    """
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        form = ContactForm(request.POST)
        if form.is_valid():
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
                return JsonResponse({"status": "OK"})
            except Exception as e:
                return JsonResponse({"status": "ERROR", "message": str(e)})
    return JsonResponse({"status": "ERROR"})


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

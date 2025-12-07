from django.shortcuts import redirect
from django.utils import timezone

from english_app.apps.core.utils import check_and_set_achievements
from english_app.apps.progress.utils import get_srs_object
from english_app.apps.core.models import Word
from english_app.apps.progress.forms import WordCheckForm

from english_app.apps.progress.constants import (
    SRS_WORD_NOT_FOUND_MSG,
    SRS_OBJECT_NOT_FOUND_MSG,
    SRS_WORD_NOT_AVAILABLE_MSG,
    SRS_FORM_ERROR_MSG,
    SRS_CORRECT_ANSWER_MSG,
    SRS_LEARNED_MSG,
    SRS_WRONG_ANSWER_MSG,
    SRS_LEARNED_THRESHOLD,
)
from redis_service import r


def handle_srs_post_request(request):
    """
    Handling a POST request to check a word in SRS
    """
    word_id = request.POST.get("check_word")

    # Receiving the word and SRS object
    word = Word.objects.filter(id=word_id, user=request.user).first()
    if not word:
        request.session["error_message"] = SRS_WORD_NOT_FOUND_MSG
        return redirect("games:srs_technique")
    srs_obj = get_srs_object(word)

    if not srs_obj:
        request.session["error_message"] = SRS_OBJECT_NOT_FOUND_MSG
        return redirect("games:dictionary")

    # Check word availability
    if srs_obj.access_timer > timezone.now():
        request.session["error_message"] = SRS_WORD_NOT_AVAILABLE_MSG
        return redirect("games:srs_technique")

    # Checking the correctness of the translation
    form = WordCheckForm(request.POST, prefix=f"word_{word.id}")
    if not form.is_valid():
        request.session["error_message"] = SRS_FORM_ERROR_MSG
        return redirect("games:srs_technique")

    user_input = form.cleaned_data["translate_input"].strip().lower()
    is_correct = user_input == word.russian_name.lower()

    # Updating the SRS status
    srs_obj.update_after_answer(failure=not is_correct)

    # Forming a message
    if is_correct:
        r.incr(f"{request.user.username}:{request.user.id}:srs_session_counter")
        r.incr(f"{request.user.username}:{request.user.id}:srs_accuracy_counter")
        check_and_set_achievements(request, "check_srs_session_count")
        check_and_set_achievements(request, "check_srs_accuracy_counter")
        if srs_obj.interval >= SRS_LEARNED_THRESHOLD:
            request.session["achievement_message"] = SRS_LEARNED_MSG.format(
                word.russian_name
            )
        else:
            request.session["default_message"] = SRS_CORRECT_ANSWER_MSG
    else:
        r.set(f"{request.user.username}:{request.user.id}:srs_accuracy_counter", 0)
        request.session["error_message"] = SRS_WRONG_ANSWER_MSG.format(
            word.russian_name
        )
    return redirect("games:srs_technique")

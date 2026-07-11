from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _

from apps.progress.constants import (
    SRS_CORRECT_ANSWER_MSG,
    SRS_LEARNED_MSG,
    SRS_WORD_NOT_AVAILABLE_MSG,
    SRS_WRONG_ANSWER_MSG,
)
from apps.progress.forms import WordCheckForm
from apps.progress.achievements import AchievementChecker
from apps.progress.models import UserSRS
from apps.statistics.models import SRSReviewLog
from redis_service import r


def handle_srs_post(request):
    """
    Handling a POST request to check a word in SRS
    """
    word_id = request.POST.get("check_word")

    srs = get_object_or_404(
        UserSRS.objects.select_related("word"),
        word_id=word_id,
        user=request.user,
    )
    word = srs.word

    if not srs.is_due:
        messages.error(request, SRS_WORD_NOT_AVAILABLE_MSG)
        return redirect("progress:srs_technique")

    form = WordCheckForm(request.POST, prefix=f"word_{word.id}")
    if not form.is_valid():
        messages.error(request, _("Incorrect form"))
        return redirect("progress:srs_technique")

    user_input = form.cleaned_data["translate_input"].strip().lower()
    is_correct = user_input == word.russian_name.strip().lower()

    if is_correct:
        r.incr(f"{request.user.username}:{request.user.id}:srs_session_counter")
        r.incr(f"{request.user.username}:{request.user.id}:srs_accuracy_counter")
    else:
        r.set(f"{request.user.username}:{request.user.id}:srs_accuracy_counter", 0)

    interval_before = srs.interval
    ease_factor_before = srs.ease_factor
    repetitions_before = srs.repetitions
    with transaction.atomic():
        learned = srs.update_after_answer(correct=is_correct)
        SRSReviewLog.objects.create(
            user=request.user,
            word=word,
            user_answer=user_input,
            correct_answer=word.russian_name,
            is_correct=is_correct,
            interval_before=interval_before,
            interval_after=srs.interval,
            ease_factor_before=ease_factor_before,
            ease_factor_after=srs.ease_factor,
            repetitions_before=repetitions_before,
            repetitions_after=srs.repetitions,
        )

    if is_correct:
        checker = AchievementChecker(request.user)
        checker.check_srs_session_count()
        checker.check_srs_accuracy_counter()

    if learned:
        messages.success(request, SRS_LEARNED_MSG.format(word.english_name))
    elif is_correct:
        messages.success(request, SRS_CORRECT_ANSWER_MSG)
    else:
        messages.error(request, SRS_WRONG_ANSWER_MSG.format(word.english_name))
    return redirect("progress:srs_technique")

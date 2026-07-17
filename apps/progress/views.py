from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import TemplateView

from apps.progress.forms import AnswerForm
from apps.progress.models import (
    Achievement,
    StudySession,
    StudySessionCard,
    UserAchievement,
)
from apps.progress.services.modes import LearningMode, is_valid_mode
from apps.progress.services.review_service import ReviewError, submit_answer
from apps.progress.services.session_service import (
    complete_session,
    get_current_card,
    get_mode_cards,
    get_session,
    get_session_counts,
    start_or_resume_session,
)


def _get_session_or_404(user, session_id):
    try:
        return get_session(user, session_id)
    except StudySession.DoesNotExist as error:
        raise Http404 from error


def _card_context(session, form=None):
    card = get_current_card(session)
    if card is None and session.status == StudySession.Status.ACTIVE:
        complete_session(session)

    counts = get_session_counts(session)
    return {
        "selected": "srs_technique",
        "session": session,
        "mode_label": LearningMode(session.mode).label,
        "card": card,
        "word": card.progress.word if card else None,
        "form": form or AnswerForm(),
        "counts": counts,
        "current_number": counts["answered"] + 1 if card else counts["total"],
        "is_audio_mode": session.mode == LearningMode.AUDIO_TO_EN,
        "is_english_prompt": session.mode == LearningMode.EN_TO_RU,
    }


def _render_session_partial(request, session, form=None):
    context = _card_context(session, form)
    template = (
        "progress/partials/study_card.html"
        if context["card"]
        else "progress/partials/session_completed.html"
    )
    return render(request, template, context)


@login_required
@require_GET
def srs_technique(request):
    return render(
        request,
        "progress/srs.html",
        {
            "selected": "srs_technique",
            "mode_cards": get_mode_cards(request.user),
        },
    )


@login_required
@require_POST
def start_learning(request, mode):
    if not is_valid_mode(mode):
        raise Http404
    session = start_or_resume_session(request.user, mode)
    if session is None:
        messages.info(request, _("There are no cards ready in this mode."))
        return redirect("progress:srs_technique")
    return redirect("progress:learning_session", session_id=session.id)


@login_required
@require_GET
def learning_session(request, session_id):
    session = _get_session_or_404(request.user, session_id)
    return render(request, "progress/session.html", _card_context(session))


@login_required
@require_POST
def answer_card(request, session_id, card_id):
    session = _get_session_or_404(request.user, session_id)
    form = AnswerForm(request.POST)
    if not form.is_valid():
        return _render_session_partial(request, session, form)

    try:
        result = submit_answer(
            request.user,
            session_id=session_id,
            card_id=card_id,
            answer=form.cleaned_data["answer"],
        )
    except (ReviewError, StudySessionCard.DoesNotExist):
        messages.error(request, _("This card has already been processed."))
        return _render_session_partial(request, session)

    session.refresh_from_db()
    context = {
        **_card_context(session),
        "result": result,
    }
    return render(request, "progress/partials/answer_result.html", context)


@login_required
@require_GET
def next_card(request, session_id):
    session = _get_session_or_404(request.user, session_id)
    return _render_session_partial(request, session)


@login_required
@require_POST
def leave_session(request, session_id):
    _get_session_or_404(request.user, session_id)
    return redirect("progress:srs_technique")


class AchievementsView(LoginRequiredMixin, TemplateView):
    template_name = "progress/achievements.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_achievements = Achievement.objects.all()
        user_achievements = UserAchievement.objects.filter(
            user=self.request.user
        ).select_related("achievement")

        earned_ids = {ua.achievement_id for ua in user_achievements}

        context["selected"] = "achievements"
        context["user_achievements"] = user_achievements
        context["available_achievements"] = [
            a for a in all_achievements if not a.is_secret and a.id not in earned_ids
        ]
        context["secret_achievements"] = [
            a for a in all_achievements if a.is_secret and a.id not in earned_ids
        ]
        return context

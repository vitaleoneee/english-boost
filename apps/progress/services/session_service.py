from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Min, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.dictionary.choices import StudyStatus
from apps.dictionary.models import Word
from apps.progress.models import (
    StudySession,
    StudySessionCard,
    UserWordModeProgress,
)
from apps.progress.services.modes import LearningMode, MODE_DETAILS

SESSION_SIZE = 20


def create_progress_for_word(word):
    completed = word.status == StudyStatus.LEARNED
    completed_at = timezone.now() if completed else None
    next_review_at = None if completed else timezone.now()
    UserWordModeProgress.objects.bulk_create(
        [
            UserWordModeProgress(
                user=word.user,
                word=word,
                mode=mode,
                completed=completed,
                completed_at=completed_at,
                next_review_at=next_review_at,
            )
            for mode in LearningMode.values
        ],
        ignore_conflicts=True,
    )


def ensure_progress_for_user(user):
    words = Word.objects.filter(user=user).only("id", "user_id", "status")
    existing = set(
        UserWordModeProgress.objects.filter(user=user).values_list("word_id", "mode")
    )
    now = timezone.now()
    missing = []
    for word in words:
        completed = word.status == StudyStatus.LEARNED
        for mode in LearningMode.values:
            if (word.id, mode) not in existing:
                missing.append(
                    UserWordModeProgress(
                        user=user,
                        word=word,
                        mode=mode,
                        completed=completed,
                        completed_at=now if completed else None,
                        next_review_at=None if completed else now,
                    )
                )
    if missing:
        UserWordModeProgress.objects.bulk_create(missing, ignore_conflicts=True)


def get_mode_cards(user):
    ensure_progress_for_user(user)
    now = timezone.now()
    active_sessions = {}
    active_query = StudySession.objects.filter(
        user=user,
        status=StudySession.Status.ACTIVE,
    ).annotate(
        pending_count=Count(
            "cards",
            filter=Q(cards__status=StudySessionCard.Status.PENDING),
        )
    )
    for session in active_query:
        if session.pending_count:
            active_sessions[session.mode] = session
        else:
            complete_session(session)
    summaries = {
        row["mode"]: row
        for row in UserWordModeProgress.objects.filter(user=user)
        .values("mode")
        .annotate(
            total=Count("id"),
            completed_count=Count("id", filter=Q(completed=True)),
            due_count=Count(
                "id",
                filter=Q(completed=False, next_review_at__lte=now),
            ),
            next_review=Min(
                "next_review_at",
                filter=Q(completed=False, next_review_at__gt=now),
            ),
        )
    }

    cards = []
    for mode, label in LearningMode.choices:
        summary = summaries.get(mode, {})
        active_session = active_sessions.get(mode)
        total = summary.get("total", 0)
        completed_count = summary.get("completed_count", 0)
        due_count = summary.get("due_count", 0)

        if active_session and active_session.pending_count:
            state = "active"
            enabled = True
            count = active_session.pending_count
            explanation = _("An unfinished session is waiting for you.")
        elif total and completed_count == total:
            state = "completed"
            enabled = False
            count = 0
            explanation = _("Mode completed.")
        elif due_count:
            state = "ready"
            enabled = True
            count = due_count
            explanation = _("Cards are ready for review.")
        elif total:
            state = "waiting"
            enabled = False
            count = 0
            explanation = _("No cards are due yet.")
        else:
            state = "empty"
            enabled = False
            count = 0
            explanation = _("Add words to your dictionary first.")

        cards.append(
            {
                "mode": mode,
                "label": label,
                "description": MODE_DETAILS[LearningMode(mode)]["description"],
                "icon": MODE_DETAILS[LearningMode(mode)]["icon"],
                "state": state,
                "enabled": enabled,
                "count": count,
                "explanation": explanation,
                "session": active_session,
                "next_review": summary.get("next_review"),
            }
        )
    return cards


@transaction.atomic
def start_or_resume_session(user, mode):
    mode = LearningMode(mode)
    get_user_model().objects.select_for_update().get(pk=user.pk)

    active = (
        StudySession.objects.select_for_update()
        .filter(user=user, mode=mode, status=StudySession.Status.ACTIVE)
        .first()
    )
    if active:
        if active.cards.filter(status=StudySessionCard.Status.PENDING).exists():
            return active
        complete_session(active)

    progress_items = list(
        UserWordModeProgress.objects.filter(
            user=user,
            mode=mode,
            completed=False,
            next_review_at__lte=timezone.now(),
        ).order_by("next_review_at", "id")[:SESSION_SIZE]
    )
    if not progress_items:
        return None

    session = StudySession.objects.create(user=user, mode=mode)
    StudySessionCard.objects.bulk_create(
        [
            StudySessionCard(session=session, progress=progress, position=position)
            for position, progress in enumerate(progress_items, start=1)
        ]
    )
    return session


def get_session(user, session_id):
    return StudySession.objects.get(pk=session_id, user=user)


def get_current_card(session):
    return (
        session.cards.filter(status=StudySessionCard.Status.PENDING)
        .select_related("progress__word")
        .order_by("position")
        .first()
    )


def get_session_counts(session):
    cards = session.cards.all()
    return {
        "total": cards.count(),
        "answered": cards.filter(status=StudySessionCard.Status.ANSWERED).count(),
        "correct": cards.filter(is_correct=True).count(),
        "incorrect": cards.filter(is_correct=False).count(),
    }


def complete_session(session):
    if session.status == StudySession.Status.COMPLETED:
        return session
    session.status = StudySession.Status.COMPLETED
    session.finished_at = timezone.now()
    session.save(update_fields=("status", "finished_at"))
    return session

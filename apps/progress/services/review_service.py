from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.progress.achievements import AchievementChecker
from apps.progress.models import StudySession, StudySessionCard
from apps.progress.services.answer_checkers import get_answer_checker
from apps.progress.services.session_service import complete_session
from apps.progress.services.srs_service import apply_answer
from apps.statistics.models import SRSReviewLog
from redis_service import r


class ReviewError(Exception):
    pass


@dataclass(frozen=True)
class ReviewResult:
    is_correct: bool
    user_answer: str
    correct_answer: str
    interval_before: int
    interval_after: int
    repetitions_before: int
    repetitions_after: int
    ease_factor_before: float
    ease_factor_after: float
    next_review_at: object
    mode_completed: bool
    session_completed: bool


def submit_answer(user, session_id, card_id, answer):
    with transaction.atomic():
        card = (
            StudySessionCard.objects.select_for_update()
            .select_related("session", "progress__word")
            .get(pk=card_id, session_id=session_id, session__user=user)
        )
        if card.session.status != StudySession.Status.ACTIVE:
            raise ReviewError("This session is already completed.")
        if card.status != StudySessionCard.Status.PENDING:
            raise ReviewError("This card has already been answered.")

        current_card_id = (
            card.session.cards.filter(status=StudySessionCard.Status.PENDING)
            .order_by("position")
            .values_list("id", flat=True)
            .first()
        )
        if current_card_id != card.id:
            raise ReviewError("This is not the current card.")

        progress = card.progress
        checked = get_answer_checker(progress.mode).check(progress.word, answer)
        interval_before = progress.interval
        repetitions_before = progress.repetitions
        ease_factor_before = progress.ease_factor
        mode_completed = apply_answer(progress, checked.is_correct)

        card.status = StudySessionCard.Status.ANSWERED
        card.is_correct = checked.is_correct
        card.answered_at = timezone.now()
        card.save(update_fields=("status", "is_correct", "answered_at"))

        SRSReviewLog.objects.create(
            user=user,
            word=progress.word,
            user_answer=checked.user_answer,
            correct_answer=checked.correct_answer,
            is_correct=checked.is_correct,
            interval_before=interval_before,
            interval_after=progress.interval,
            ease_factor_before=ease_factor_before,
            ease_factor_after=progress.ease_factor,
            repetitions_before=repetitions_before,
            repetitions_after=progress.repetitions,
        )

        session_completed = not card.session.cards.filter(
            status=StudySessionCard.Status.PENDING
        ).exists()
        if session_completed:
            complete_session(card.session)

        result = ReviewResult(
            is_correct=checked.is_correct,
            user_answer=checked.user_answer,
            correct_answer=checked.correct_answer,
            interval_before=interval_before,
            interval_after=progress.interval,
            repetitions_before=repetitions_before,
            repetitions_after=progress.repetitions,
            ease_factor_before=ease_factor_before,
            ease_factor_after=progress.ease_factor,
            next_review_at=progress.next_review_at,
            mode_completed=mode_completed,
            session_completed=session_completed,
        )

    _update_achievements(user, checked.is_correct)
    return result


def _update_achievements(user, is_correct):
    session_key = f"{user.username}:{user.id}:srs_session_counter"
    accuracy_key = f"{user.username}:{user.id}:srs_accuracy_counter"
    if is_correct:
        r.incr(session_key)
        r.incr(accuracy_key)
        checker = AchievementChecker(user)
        checker.check_srs_session_count()
        checker.check_srs_accuracy_counter()
    else:
        r.set(accuracy_key, 0)

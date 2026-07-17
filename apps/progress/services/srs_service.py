import math
from datetime import timedelta

from django.utils import timezone

from apps.dictionary.choices import StudyStatus
from apps.progress.constants import SRS_LEARNED_THRESHOLD
from apps.progress.models import UserWordModeProgress
from apps.progress.services.modes import LearningMode


def apply_answer(progress, is_correct):
    now = timezone.now()

    if is_correct:
        if progress.repetitions == 0:
            progress.interval = 1
        elif progress.repetitions == 1:
            progress.interval = 6
        else:
            progress.interval = math.ceil(progress.interval * progress.ease_factor)

        progress.repetitions += 1
        progress.ease_factor = min(3.0, progress.ease_factor + 0.1)

        if progress.interval >= SRS_LEARNED_THRESHOLD:
            progress.completed = True
            progress.completed_at = now
            progress.next_review_at = None
        else:
            progress.next_review_at = now + timedelta(days=progress.interval)
    else:
        progress.repetitions = 0
        progress.interval = 1
        progress.ease_factor = max(1.3, progress.ease_factor - 0.2)
        progress.next_review_at = now + timedelta(days=1)

    progress.save(
        update_fields=(
            "interval",
            "repetitions",
            "ease_factor",
            "next_review_at",
            "completed",
            "completed_at",
            "updated_at",
        )
    )
    update_word_status(progress.word)
    return progress.completed


def update_word_status(word):
    all_modes_completed = (
        UserWordModeProgress.objects.filter(word=word).count()
        == len(LearningMode.values)
        and not UserWordModeProgress.objects.filter(
            word=word,
            completed=False,
        ).exists()
    )
    new_status = StudyStatus.LEARNED if all_modes_completed else StudyStatus.PROCESS
    if word.status != new_status:
        word.status = new_status
        word.save(update_fields=("status",))

from datetime import timedelta

from django.db.models import Case, Count, IntegerField, Q, Sum, When
from django.utils import timezone
from django.utils.translation import gettext as _, ngettext

from apps.dictionary.choices import StudyStatus
from apps.dictionary.models import Word
from apps.progress.models import UserSRS
from apps.statistics.models import SRSReviewLog


def _accuracy(logs):
    total = logs.count()
    if not total:
        return None
    return round(logs.filter(is_correct=True).count() * 100 / total)


def _learning_streak(activity_dates, today):
    """Return the consecutive-day streak ending today or yesterday."""
    active = set(activity_dates)
    cursor = today
    if cursor not in active:
        cursor -= timedelta(days=1)

    streak = 0
    while cursor in active:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def build_statistics(user):
    """Build durable learning analytics from review history and current SRS state."""
    now = timezone.now()
    today = timezone.localdate(now)
    start_30_days = today - timedelta(days=29)
    start_7_days = today - timedelta(days=6)
    logs = SRSReviewLog.objects.filter(user=user)
    recent_logs = logs.filter(reviewed_at__date__gte=start_30_days)
    activity_rows = (
        recent_logs.values("reviewed_at__date")
        .annotate(
            count=Count("id"),
            correct=Sum(
                Case(
                    When(is_correct=True, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        .order_by("reviewed_at__date")
    )
    activity_by_day = {row["reviewed_at__date"]: row for row in activity_rows}
    activity = []
    for offset in range(30):
        day = start_30_days + timedelta(days=offset)
        row = activity_by_day.get(day, {})
        count = row.get("count", 0)
        correct = row.get("correct", 0) or 0
        activity.append(
            {
                "label": day.strftime("%d.%m"),
                "count": count,
                "accuracy": round(correct * 100 / count) if count else None,
            }
        )

    active_dates = logs.values_list("reviewed_at__date", flat=True).distinct()
    queue = UserSRS.objects.filter(user=user)
    due_now = queue.filter(access_timer__lte=now).count()
    waiting = queue.filter(access_timer__gt=now).count()
    weak_words = list(
        logs.values("word_id", "word__english_name", "word__russian_name")
        .annotate(
            attempts=Count("id"),
            mistakes=Count("id", filter=Q(is_correct=False)),
            correct=Sum(
                Case(
                    When(is_correct=True, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
        )
        .filter(attempts__gte=2)
        .order_by("-mistakes", "correct")[:5]
    )
    for word in weak_words:
        word["accuracy"] = round((word["correct"] or 0) * 100 / word["attempts"])
    weak_words = [
        word for word in weak_words if word["mistakes"] >= 2 or word["accuracy"] < 70
    ]

    if due_now:
        next_action = {
            "title": ngettext(
                "%(count)d word is ready for review",
                "%(count)d words are ready for review",
                due_now,
            )
            % {"count": due_now},
            "text": _(
                "Review them now to protect your memory and keep your streak alive."
            ),
            "url": "progress:srs_technique",
            "button": _("Start review"),
        }
    elif weak_words:
        next_action = {
            "title": _("Your weak words need attention"),
            "text": _(
                "Open the review queue when they are due and focus on the words below."
            ),
            "url": "progress:srs_technique",
            "button": _("Open SRS queue"),
        }
    else:
        next_action = {
            "title": _("You are up to date"),
            "text": _(
                "Come back when the next words become ready, or add a new word to keep building your vocabulary."
            ),
            "url": "dictionary:dictionary-list",
            "button": _("Open dictionary"),
        }

    return {
        "has_reviews": logs.exists(),
        "streak": _learning_streak(active_dates, today),
        "learned_words": Word.objects.filter(
            user=user, status=StudyStatus.LEARNED
        ).count(),
        "in_progress_words": Word.objects.filter(
            user=user, status=StudyStatus.PROCESS
        ).count(),
        "reviews_today": logs.filter(reviewed_at__date=today).count(),
        "reviews_week": logs.filter(reviewed_at__date__gte=start_7_days).count(),
        "reviews_month": recent_logs.count(),
        "accuracy_overall": _accuracy(logs),
        "accuracy_7_days": _accuracy(logs.filter(reviewed_at__date__gte=start_7_days)),
        "accuracy_30_days": _accuracy(recent_logs),
        "due_now": due_now,
        "waiting": waiting,
        "queue_total": due_now + waiting,
        "weak_words": weak_words,
        "activity": activity,
        "next_action": next_action,
    }

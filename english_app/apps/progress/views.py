from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from english_app.apps.core.utils import check_and_set_achievements
from english_app.apps.progress.models import UserSRS, Achievement, UserAchievement
from english_app.apps.progress.forms import WordCheckForm
from english_app.apps.progress.services.srs_handlers import handle_srs_post_request


@login_required
def srs_technique(request):
    """
    SRS technology implementation controller
    """
    if request.method == "POST":
        return handle_srs_post_request(request)
    # Getting a list of unstudied words
    srs_items = UserSRS.objects.filter(
        user=request.user, word__status="PROCESS"
    ).select_related("word")

    # Word form repository with "Check" button
    word_forms = []

    for srs in srs_items:
        word = srs.word
        total_seconds, access_time_str = srs.get_access_delay()
        # Add to form store
        word_forms.append(
            {
                "word": word,
                "form": WordCheckForm(prefix=f"word_{word.id}"),
                "access_time": access_time_str,
                "access_time_seconds": total_seconds,
            }
        )
    word_forms.sort(key=lambda w: w["access_time_seconds"])
    achievement_message = request.session.pop("achievement_message", None)
    default_message = request.session.pop("default_message", None)
    error_message = request.session.pop("error_message", None)
    return render(
        request,
        "games/srs.html",
        {
            "selected": "srs_technique",
            "word_forms": word_forms,
            "achievement_message": achievement_message,
            "default_message": default_message,
            "error_message": error_message,
        },
    )


@login_required
def get_achievements(request):
    """
    Achievement receiving and processing controller
    """
    check_and_set_achievements(request, "check_day_count")
    achievements = Achievement.objects.all()
    user_achievements = UserAchievement.objects.filter(
        user=request.user, achievement__in=achievements
    )
    user_achievement_names = [ua.achievement.name for ua in user_achievements]
    secret_achievements = [a for a in achievements if a.secret]
    achievement_message = request.session.pop("achievement_message", None)
    return render(
        request,
        "games/achievements.html",
        {
            "achievements": achievements,
            "user_achievements": user_achievements,
            "user_achievement_names": user_achievement_names,
            "selected": "achievements",
            "achievement_message": achievement_message,
            "secret_achievements": secret_achievements,
        },
    )

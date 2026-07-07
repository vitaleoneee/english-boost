from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from apps.progress.forms import WordCheckForm
from apps.progress.models import UserSRS, Achievement, UserAchievement
from apps.progress.services.srs_handlers import handle_srs_post_request


@login_required
def srs_technique(request):
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
        "progress/srs.html",
        {
            "selected": "srs_technique",
            "word_forms": word_forms,
            "achievement_message": achievement_message,
            "default_message": default_message,
            "error_message": error_message,
        },
    )


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

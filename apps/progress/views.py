from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from django_htmx.http import trigger_client_event

from apps.progress.forms import WordCheckForm
from apps.progress.models import UserSRS, Achievement, UserAchievement
from apps.progress.services.srs_handlers import handle_srs_post

SRS_PAGE_SIZE = 20


def get_srs_context(request, page_number=None):
    srs_items = (
        UserSRS.objects.filter(user=request.user, word__status="PROCESS")
        .select_related("word")
        .order_by("access_timer")
    )

    paginator = Paginator(srs_items, SRS_PAGE_SIZE)
    srs_page = paginator.get_page(page_number)
    word_forms = [
        {
            "srs": srs,
            "word": srs.word,
            "form": WordCheckForm(prefix=f"word_{srs.word.id}"),
            "seconds_until_due": srs.seconds_until_due,
            "is_due": srs.is_due,
        }
        for srs in srs_page
    ]
    due_count = srs_items.filter(access_timer__lte=timezone.now()).count()
    total_count = paginator.count

    return {
        "selected": "srs_technique",
        "word_forms": word_forms,
        "srs_page": srs_page,
        "srs_total_count": total_count,
        "srs_due_count": due_count,
        "srs_waiting_count": total_count - due_count,
    }


@login_required
def srs_technique(request):
    if request.method == "POST":
        response = handle_srs_post(request)
        if response is not None:
            return response

        context = get_srs_context(request, request.POST.get("page"))
        response = render(request, "progress/partials/srs_content.html", context)
        trigger_client_event(response, "srsReviewed")
        return response

    return render(
        request,
        "progress/srs.html",
        get_srs_context(request, request.GET.get("page")),
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

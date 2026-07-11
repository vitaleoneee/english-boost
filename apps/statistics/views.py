from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.statistics.services import build_statistics


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = "statistics/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statistics = build_statistics(self.request.user)
        context.update(statistics)
        context["selected"] = "statistics"
        context["activity_chart"] = statistics["activity"]
        return context

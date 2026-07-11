from django.urls import path

from apps.statistics.views import StatisticsView

app_name = "statistics"

urlpatterns = [
    path("", StatisticsView.as_view(), name="statistics"),
]

from django.urls import path

from apps.progress.views import srs_technique, AchievementsView

app_name = "progress"

urlpatterns = [
    path("", srs_technique, name="srs_technique"),
    path("achievements/", AchievementsView.as_view(), name="achievements"),
]

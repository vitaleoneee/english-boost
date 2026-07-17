from django.urls import path

from apps.progress.views import (
    AchievementsView,
    answer_card,
    learning_session,
    leave_session,
    next_card,
    srs_technique,
    start_learning,
)

app_name = "progress"

urlpatterns = [
    path("", srs_technique, name="srs_technique"),
    path("<str:mode>/start/", start_learning, name="start_learning"),
    path("session/<int:session_id>/", learning_session, name="learning_session"),
    path(
        "session/<int:session_id>/answer/<int:card_id>/",
        answer_card,
        name="answer_card",
    ),
    path("session/<int:session_id>/next/", next_card, name="next_card"),
    path("session/<int:session_id>/leave/", leave_session, name="leave_session"),
    path("achievements/", AchievementsView.as_view(), name="achievements"),
]

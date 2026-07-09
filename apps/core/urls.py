from django.urls import path

from apps.core.views import (
    IndexView,
    ToastView,
    mark_achievements_seen,
    send_features_view,
)

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("toasts/", ToastView.as_view(), name="toasts"),
    path("achievements/seen/", mark_achievements_seen, name="mark-achievements-seen"),
    # HTMX form processing route
    path("send-features/", send_features_view, name="send-features"),
]

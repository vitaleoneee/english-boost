from django.urls import path

from apps.core.views import (
    IndexView,
    ToastView,
    send_features_view,
)

app_name = "core"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("toasts/", ToastView.as_view(), name="toasts"),

    # HTMX form processing route
    path("send-features/", send_features_view, name="send-features"),
]

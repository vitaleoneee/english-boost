from django.urls import path

from apps.support import views

app_name = "support"

urlpatterns = [
    path("requests/", views.support_request_collection, name="request-collection"),
    path(
        "requests/<int:request_id>/",
        views.support_request_detail,
        name="request-detail",
    ),
    path(
        "requests/<int:request_id>/close/",
        views.support_request_close,
        name="request-close",
    ),
    path(
        "requests/<int:request_id>/rating/",
        views.support_request_rating,
        name="request-rating",
    ),
]

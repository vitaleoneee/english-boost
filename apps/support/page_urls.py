from django.urls import path

from apps.support import views

app_name = "support_pages"

urlpatterns = [
    path("moderator/", views.moderator_dashboard, name="moderator-dashboard"),
]

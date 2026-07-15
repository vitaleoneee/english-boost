from allauth.account import views as account_views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin site route
    path("admin/", admin.site.urls),
    # Include core application route
    path("", include("apps.core.urls"), name="core"),
    # Include dictionary application route
    path("dictionary/", include("apps.dictionary.urls"), name="dictionary"),
    # Include progress & statistics application route
    path("progress/", include("apps.progress.urls"), name="progress"),
    path("progress/statistics/", include("apps.statistics.urls"), name="statistics"),
    # Support API routes
    path("support/api/", include("apps.support.urls")),
    path("support/", include("apps.support.page_urls")),
    # Auth route
    path("accounts/signup/", account_views.signup, name="account_signup"),
    path("accounts/login/", account_views.login, name="account_login"),
    path("accounts/logout/", account_views.logout, name="account_logout"),
    path("i18n/", include("django.conf.urls.i18n")),
    path(
        "accounts/password/reset/",
        account_views.password_reset,
        name="account_reset_password",
    ),
    path(
        "accounts/password/reset/done/",
        account_views.password_reset_done,
        name="account_reset_password_done",
    ),
    path(
        "accounts/password/reset/key/<uidb36>-<key>/",
        account_views.password_reset_from_key,
        name="account_reset_password_from_key",
    ),
    path(
        "accounts/password/reset/key/done/",
        account_views.password_reset_from_key_done,
        name="account_reset_password_from_key_done",
    ),
]

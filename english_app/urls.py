from django.contrib import admin
from django.urls import path, include
from allauth.account import views as account_views

urlpatterns = [
    # Admin site route
    path('admin/', admin.site.urls),

    # Include core application route
    path('', include('english_app.apps.core.urls'), name='core'),

    # Include games application route
    path('progress/', include('english_app.apps.progress.urls'), name='progress'),

    # Auth route
    path('accounts/signup/', account_views.signup, name='account_signup'),
    path('accounts/login/', account_views.login, name='account_login'),
    path('accounts/logout/', account_views.logout, name='account_logout'),
    path('accounts/password/reset/', account_views.password_reset, name='account_reset_password'),
    path('accounts/password/reset/done/', account_views.password_reset_done, name='account_reset_password_done'),
    path('accounts/password/reset/key/<uidb36>-<key>/', account_views.password_reset_from_key,
         name='account_reset_password_from_key'),
    path('accounts/password/reset/key/done/', account_views.password_reset_from_key_done,
         name='account_reset_password_from_key_done')
]

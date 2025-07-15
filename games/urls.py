from django.urls import path
from games.views import srs_technique, get_achievements

app_name = 'games'

urlpatterns = [
    path('', srs_technique, name='srs_technique'),
    path('achievements/', get_achievements, name='achievements'),
]
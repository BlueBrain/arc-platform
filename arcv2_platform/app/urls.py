from django.urls import path
from arcv2_platform.app import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('start/', views.start, name="start"),
    path('impressum/', views.impressum, name="impressum"),
    path('status/version', views.InfoVersionView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

from django.urls import path

from core_api.views.speed.list import SpeedListView

urlpatterns = [
    path("", SpeedListView.as_view()),
]

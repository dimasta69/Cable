from django.urls import path

from core_api.views.line_type.list import LineTypeListView

urlpatterns = [
    path("", LineTypeListView.as_view()),
]

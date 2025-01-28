from django.urls import path

from core_api.views.line_type.line_type_list import LineTypeListView

urlpatterns = [
    path("", LineTypeListView.as_view()),
]

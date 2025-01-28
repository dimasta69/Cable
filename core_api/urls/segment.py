from django.urls import path

from core_api.views.segment.list import SegmentListView

urlpatterns = [
    path("", SegmentListView.as_view()),
]
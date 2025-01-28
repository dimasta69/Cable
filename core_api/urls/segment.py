from django.urls import path

from core_api.views.segment.list import SegmentListView
from core_api.views.segment.segment import SegmentView

urlpatterns = [
    path("", SegmentListView.as_view()),
    path("<int:id>/", SegmentView.as_view()),
]
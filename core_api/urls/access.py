from django.urls import path

from core_api.views.access.access import AccessView
from core_api.views.access.list import AccessListView, AccessMoreView

urlpatterns = [
    path('', AccessListView.as_view()),
    path('<int:id>/', AccessView.as_view()),
    path('more/', AccessMoreView.as_view()),
]

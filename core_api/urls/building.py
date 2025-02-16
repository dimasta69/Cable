from django.urls import path

from core_api.views.building.building import BuildingView
from core_api.views.building.list import BuildingListView
from core_api.views.building.refresh_connection import RefreshBildingsConnectionView

urlpatterns = [
    path('', BuildingListView.as_view()),
    path('<int:id>/', BuildingView.as_view()),
    path('refresh/', RefreshBildingsConnectionView.as_view()),
]

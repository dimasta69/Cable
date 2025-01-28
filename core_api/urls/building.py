from django.urls import path

from core_api.views.building.building import BuildingView
from core_api.views.building.building_list import BuildingListView

urlpatterns = [
    path('', BuildingListView.as_view()),
    path('<int:id>/', BuildingView.as_view()),
]

from django.urls import path

from core_api.views.equipment.equipment_list import EquipmentsFromMapListView
from core_api.views.map.map import MapRefreshView
from core_api.views.map.map_list import MapListView
from core_api.views.map.equipment_list import EquipmentListView as EquipmentListMapView
from core_api.views.map.equipment import EquipmentView as EquipmentMapView




urlpatterns = [
    path("", MapListView.as_view()),
    path("refresh/<int:id>/", MapRefreshView.as_view()),
    path("equipments_scheme/", EquipmentListMapView.as_view()),
    path("equipments/", EquipmentsFromMapListView.as_view()),
    path("equipment_scheme/<int:id>/", EquipmentMapView.as_view()),
]

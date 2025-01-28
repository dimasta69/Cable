from django.urls import path

from core_api.views.equipment.add_equipment_for_unit import AddEquipmentForUnitView
from core_api.views.equipment.equipment import ReleaseEquipmentView, EquipmentView
from core_api.views.equipment.equipment_list import EquipmentListView
from core_api.views.equipment.equipment_to_room import AddEquipmentRoomView
from core_api.views.port_template.port_template import PortShipView

urlpatterns = [
    path('', EquipmentListView.as_view()),
    path('<int:id>/', EquipmentView.as_view()),
    path('<int:id>/add_equipment_for_unit/', AddEquipmentForUnitView.as_view()),
    path('add_room/', AddEquipmentRoomView.as_view()),
    path('release/<int:id>/', ReleaseEquipmentView.as_view()),
    path('<int:id>/port_ship/', PortShipView.as_view()),
]
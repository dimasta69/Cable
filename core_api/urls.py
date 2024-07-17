from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from core_api.views.auth.login import TokenCreateView
from core_api.views.auth.logout import TokenDestroyView
from core_api.views.scheme.scheme_list import SchemeListView
from core_api.views.scheme.scheme import SchemeView
from core_api.views.port_template.port_template_list import PortTemplateListView
from core_api.views.port_template.port_template import PortTemplateView
from core_api.views.manufacturer.manufacturer import ManufacturerView
from core_api.views.manufacturer.manufacturer_list import ManufacturerListView
from core_api.views.equipment_template.equipment_tamplate_list import EquipmentTemplateListView
from core_api.views.equipment_template.equipment_template import EquipmentTemplateView
from core_api.views.equipment.equipment import EquipmentView
from core_api.views.equipment.equipment_list import EquipmentListView
from core_api.views.equipment.add_equipment_for_unit import AddEquipmentForUnitView
from core_api.views.equipment.create_from_room import CreateEquipmentFromRoomView
from core_api.views.port.port_list import PortListView
from core_api.views.port.port import PortView
from core_api.views.port.connection_pigtail import ConnectionPigtailView
from core_api.views.port.add_sfp import AddSfpView
from core_api.views.building.building_list import BuildingListView
from core_api.views.building.building import BuildingView
from core_api.views.room.room_list import RoomListView
from core_api.views.room.room import RoomView
from core_api.views.server_rack.server_rack_list import ServerRackListView
from core_api.views.server_rack.server_rack import ServerRackView
from core_api.views.sfp_template.sfp_template_list import SfpTemplateListView
from core_api.views.sfp_template.sfp_template import SfpTemplateView
from core_api.views.sfp_template.adding_to_port import AddingToPortSfpTemplateView


schema_view = get_schema_view(
    openapi.Info(
        title='core-api',
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view()),
    path('scheme/', SchemeListView.as_view()),
    path('scheme/<int:id>/', SchemeView.as_view()),
    path('port_template/', PortTemplateListView.as_view()),
    path('port_template/<int:id>/', PortTemplateView.as_view()),
    path('manufacturer/', ManufacturerListView.as_view()),
    path('manufacturer/<int:id>/', ManufacturerView.as_view()),
    path('equipment_template/', EquipmentTemplateListView.as_view()),
    path('equipment_template/<int:id>/', EquipmentTemplateView.as_view()),
    path('equipment/', EquipmentListView.as_view()),
    path('equipment/<int:id>/', EquipmentView.as_view()),
    path('equipment/<int:id>/add_equipment_for_unit/', AddEquipmentForUnitView.as_view()),
    path('equipment/create_from_room/', CreateEquipmentFromRoomView.as_view()),
    path('port/', PortListView.as_view()),
    path('port/<int:id>/', PortView.as_view()),
    path('port/<int:id>/connection_pigtail/', ConnectionPigtailView.as_view()),
    path('port/<int:id>/add_sfp/', AddSfpView.as_view()),
    path('building/', BuildingListView.as_view()),
    path('building/<int:id>/', BuildingView.as_view()),
    path('room/', RoomListView.as_view()),
    path('room/<int:id>/', RoomView.as_view()),
    path('server_rack/', ServerRackListView.as_view()),
    path('server_rack/<int:id>/', ServerRackView.as_view()),
    path('sfp_template/', SfpTemplateListView.as_view()),
    path('sfp_template/<int:id>/', SfpTemplateView.as_view()),
    path('sfp_template/<int:id>/adding_to_port/', AddingToPortSfpTemplateView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

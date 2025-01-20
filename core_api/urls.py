from django.conf.urls.static import static
from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from cabel.settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT
from core_api.views.access.access import AccessView
from core_api.views.auth.login import TokenCreateView
from core_api.views.auth.logout import TokenDestroyView
from core_api.views.scheme.scheme_list import SchemeListView
from core_api.views.scheme.scheme import SchemeView
from core_api.views.port_template.port_template_list import PortTemplateListView
from core_api.views.port_template.port_template import PortTemplateView, ConnectionPortShipView
from core_api.views.manufacturer.manufacturer import ManufacturerView
from core_api.views.manufacturer.manufacturer_list import ManufacturerListView
from core_api.views.equipment_template.equipment_tamplate_list import EquipmentTemplateListView
from core_api.views.equipment_template.equipment_template import EquipmentTemplateView
from core_api.views.equipment.equipment import EquipmentView
from core_api.views.equipment.equipment_list import EquipmentListView, EquipmentsFromMapListView
from core_api.views.equipment.add_equipment_for_unit import AddEquipmentForUnitView
from core_api.views.port.port_list import PortListView
from core_api.views.port.port import PortView
from core_api.views.port.connection_pigtail import ConnectionPigtailView
from core_api.views.port.connection_pigtail_list import ConnectionPigtailListView
from core_api.views.port.disconnect_sfp import DisconnectSfpView
from core_api.views.port.disconnect_pigtail import DisconnectPigtailView
from core_api.views.port.disconnect_port_list import DisconnectPortListView
from core_api.views.port.add_sfp import AddSfpView
from core_api.views.port.connection import ConnectionView, DisconnectionView
from core_api.views.building.building_list import BuildingListView
from core_api.views.building.building import BuildingView
from core_api.views.room.room_list import RoomListView
from core_api.views.room.room import RoomView
from core_api.views.server_rack.server_rack_list import ServerRackListView
from core_api.views.server_rack.server_rack import ServerRackView
from core_api.views.sfp_template.sfp_template_list import SfpTemplateListView
from core_api.views.sfp_template.sfp_template import SfpTemplateView
from core_api.views.sfp_template.adding_to_port import AddingToPortSfpTemplateView
from core_api.views.access.access_list import AccessListView
from core_api.views.type_port.type_port_list import TypePortListView
from core_api.views.users.users_list import UsersListView
from core_api.views.equipment_type.equipment_type_list import ListEquipmentTypeView
from core_api.views.line_type.line_type_list import LineTypeListView
from core_api.views.speed.list import SpeedListView
from core_api.views.equipment.equipment_to_room import AddEquipmentRoomView
from core_api.views.equipment.equipment import ReleaseEquipmentView
from core_api.views.port_template.port_template import PortShipView
from core_api.views.map.map import MapView
from core_api.views.map.map_list import MapListView
from core_api.views.map.equipment_list import EquipmentListView as EquipmentListMapView
from core_api.views.map.equipment import EquipmentView as EquipmentMapView

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
    path('equipment_type/', ListEquipmentTypeView.as_view()),
    path('equipment/add_room/', AddEquipmentRoomView.as_view()),
    path('port/', PortListView.as_view()),
    path('port/<int:id>/', PortView.as_view()),
    path('port/<int:id>/connection_pigtail/', ConnectionPigtailView.as_view()),
    path('port/connection_pigtail_list/', ConnectionPigtailListView.as_view()),
    path('port/<int:id>/add_sfp/', AddSfpView.as_view()),
    path('port/disconnect_sfp/', DisconnectSfpView.as_view()),
    path('port/disconnect_pigtail/', DisconnectPigtailView.as_view()),
    path('port/disconnect_port_list/', DisconnectPortListView.as_view()),
    path('equipment/release/<int:id>/', ReleaseEquipmentView.as_view()),
    path('building/', BuildingListView.as_view()),
    path('building/<int:id>/', BuildingView.as_view()),
    path('room/', RoomListView.as_view()),
    path('room/<int:id>/', RoomView.as_view()),
    path('server_rack/', ServerRackListView.as_view()),
    path('server_rack/<int:id>/', ServerRackView.as_view()),
    path('sfp_template/', SfpTemplateListView.as_view()),
    path('sfp_template/<int:id>/', SfpTemplateView.as_view()),
    path('sfp_template/<int:id>/adding_to_port/', AddingToPortSfpTemplateView.as_view()),
    path('access/', AccessListView.as_view()),
    path('access/<int:id>/', AccessView.as_view()),
    path('type_port/', TypePortListView.as_view()),
    path('users_list/', UsersListView.as_view()),
    path('connection_port_ship/', ConnectionPortShipView.as_view()),
    path('equipment/<int:id>/port_ship/', PortShipView.as_view()),
    path("connection/", ConnectionView.as_view()),
    path("disconnection/", DisconnectionView.as_view()),
    path("speed/", SpeedListView.as_view()),
    path("line_type/", LineTypeListView.as_view()),
    path("map/", MapView.as_view()),
    path("maps/", MapListView.as_view()),
    path("maps/equipments_scheme/", EquipmentListMapView.as_view()),
    path("maps/equipments/", EquipmentsFromMapListView.as_view()),
    path("maps/equipment_scheme/", EquipmentMapView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)


from django.urls import path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

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
from core_api.views.port.port_list import PortListView
from core_api.views.port.port import PortView

schema_view = get_schema_view(
    openapi.Info(
        title='core-api',
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
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
    path('port/', PortListView.as_view()),
    path('port/<int:id>/', PortView.as_view()),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

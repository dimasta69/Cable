from django.conf.urls.static import static
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from cabel.settings import MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT


urlpatterns = [
    path('auth/', include("core_api.urls.auth")),
    path('scheme/', include("core_api.urls.scheme")),
    path('port_template/', include("core_api.urls.port_template")),
    path('manufacturer/', include("core_api.urls.manufacturer")),
    path('equipment_template/', include("core_api.urls.equipment_template")),
    path('equipment/', include("core_api.urls.equipment")),
    path('equipment_type/', include("core_api.urls.equipment_type")),
    path('port/', include("core_api.urls.port")),
    path('building/', include("core_api.urls.building")),
    path('room/', include("core_api.urls.room")),
    path('server_rack/', include("core_api.urls.server_rack")),
    path('sfp_template/', include("core_api.urls.sfp_template")),
    path('access/', include("core_api.urls.access")),
    path('type_port/', include("core_api.urls.type_port")),
    path('users_list/', include("core_api.urls.users_list")),
    path('connection_port_ship/', include("core_api.urls.connection_port_ship")),
    path("connection/", include("core_api.urls.connection")),
    path("disconnection/", include("core_api.urls.disconnection")),
    path("speed/", include("core_api.urls.speed")),
    path("line_type/", include("core_api.urls.line_type")),
    path("map/", include("core_api.urls.map")),
    path("segment/", include("core_api.urls.segment")),
    path("vlan_device/", include("core_api.urls.vlan_device")),
    path("vlan/", include("core_api.urls.vlan")),
    path("port_mode/", include("core_api.urls.port_mode")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)


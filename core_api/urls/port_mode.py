from django.urls import path

from core_api.views.port_mode.list import PortModeListView

urlpatterns = [
    path("", PortModeListView.as_view())
]
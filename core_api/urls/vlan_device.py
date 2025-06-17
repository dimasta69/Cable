from django.urls import path

from core_api.views.vlan_device.list import VlanDeviceListView
from core_api.views.vlan_device.vlan_device import VlanDeviceView


urlpatterns = [
    path("", VlanDeviceListView.as_view()),
    path("<int:id>/", VlanDeviceView.as_view()),
]

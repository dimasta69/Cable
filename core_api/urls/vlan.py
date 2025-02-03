from django.urls import path

from core_api.views.vlan.list import VlanListView

urlpatterns = [
    path("", VlanListView.as_view())
]

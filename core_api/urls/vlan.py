from django.urls import path

from core_api.views.vlan.list import VlanListView
from core_api.views.vlan.vlan import VlanView

urlpatterns = [
    path("", VlanListView.as_view()),
    path("<int:id>/", VlanView.as_view()),
]

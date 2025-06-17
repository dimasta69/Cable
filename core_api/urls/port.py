from django.urls import path

from core_api.views.port.disconnect_sfp import DisconnectSfpView
from core_api.views.port.port import PortView
from core_api.views.port.list import PortListView

urlpatterns = [
    path('', PortListView.as_view()),
    path('<int:id>/', PortView.as_view()),
    path('disconnect_sfp/', DisconnectSfpView.as_view()),
]

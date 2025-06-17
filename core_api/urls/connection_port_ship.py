from django.urls import path

from core_api.views.port_template.port_template import ConnectionPortShipView

urlpatterns = [
    path('', ConnectionPortShipView.as_view()),
]

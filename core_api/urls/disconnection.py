from django.urls import path

from core_api.views.port.connection import DisconnectionView

urlpatterns = [
    path("", DisconnectionView.as_view()),
]

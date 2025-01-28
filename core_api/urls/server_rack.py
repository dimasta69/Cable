from django.urls import path

from core_api.views.server_rack.server_rack import ServerRackView
from core_api.views.server_rack.server_rack_list import ServerRackListView

urlpatterns = [
    path('', ServerRackListView.as_view()),
    path('<int:id>/', ServerRackView.as_view()),
]

from django.urls import path

from core_api.views.manufacturer.manufacturer import ManufacturerView
from core_api.views.manufacturer.manufacturer_list import ManufacturerListView

urlpatterns = [
    path('', ManufacturerListView.as_view()),
    path('<int:id>/', ManufacturerView.as_view()),
]

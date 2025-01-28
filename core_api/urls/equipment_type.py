from django.urls import path

from core_api.views.equipment_type.equipment_type_list import ListEquipmentTypeView

urlpatterns = [
    path('', ListEquipmentTypeView.as_view()),
]

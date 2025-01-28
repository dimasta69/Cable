from django.urls import path

from core_api.views.equipment_template.equipment_tamplate_list import EquipmentTemplateListView
from core_api.views.equipment_template.equipment_template import EquipmentTemplateView

urlpatterns = [
    path('', EquipmentTemplateListView.as_view()),
    path('<int:id>/', EquipmentTemplateView.as_view()),
]

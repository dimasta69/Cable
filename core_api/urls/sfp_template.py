from django.urls import path

from core_api.views.sfp_template.adding_to_port import AddingToPortSfpTemplateView
from core_api.views.sfp_template.sfp_template import SfpTemplateView
from core_api.views.sfp_template.sfp_template_list import SfpTemplateListView

urlpatterns = [
    path('', SfpTemplateListView.as_view()),
    path('<int:id>/', SfpTemplateView.as_view()),
    path('<int:id>/adding_to_port/', AddingToPortSfpTemplateView.as_view()),
]

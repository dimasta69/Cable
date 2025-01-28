from django.urls import path

from core_api.views.port_template.port_template import PortTemplateView
from core_api.views.port_template.port_template_list import PortTemplateListView

urlpatterns = [
    path('', PortTemplateListView.as_view()),
    path('<int:id>/', PortTemplateView.as_view()),
]

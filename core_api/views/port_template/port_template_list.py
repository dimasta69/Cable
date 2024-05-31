from rest_framework.views import APIView
from rest_framework.response import Response

from models_app.models.port_template import PortTemplate
from core_api.serializers.port_template.port_template_list import PortTemplateListSerializer
from core_api.services.port_template.port_template_list import PortTemplateListService
from rest_framework.permissions import IsAuthenticated
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class PortTemplateView(APIView):
    serializers_class = PortTemplateListSerializer
    model = PortTemplate
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(PortTemplateListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': PortTemplateListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

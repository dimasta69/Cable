from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from models_app.models.port.port_template.models import PortTemplate
from core_api.serializers.port_template.port_template_list import PortTemplateListSerializer
from core_api.services.port_template.port_template_list import PortTemplateListService
from core_api.services.port_template.create import CreatePortTemplateService
from core_api.serializers.port_template.create_port_template import CreatePortTemplateSerializer
from core_api.swagger_scheme.port_template import port_template_list, create_port_template
from rest_framework.permissions import IsAuthenticated
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class PortTemplateListView(APIView):
    serializer_class = CreatePortTemplateSerializer
    queryset = PortTemplate.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**port_template_list)
    def get(self, request):
        outcome = ServiceOutcome(PortTemplateListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': PortTemplateListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    @swagger_auto_schema(**create_port_template)
    def post(self, request):
        outcome = ServiceOutcome(CreatePortTemplateService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)

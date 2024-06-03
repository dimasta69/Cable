from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from models_app.models.port_template import PortTemplate
from core_api.services.port_template.port_template import PortTemplateService
from core_api.serializers.port_template.port_template_list import PortTemplateListSerializer
from core_api.services.port_template.update import UpdatePortTemplateService
from core_api.services.port_template.delete import PortTemplateDeleteService
from core_api.swagger_scheme.port_template import port_temple, update_port_template, delete_port_template


class PortTemplateView(APIView):
    serializer_class = PortTemplateListSerializer
    permission_classes = [IsAuthenticated]
    queryset = PortTemplate.objects.all()

    @swagger_auto_schema(**port_temple)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(PortTemplateService, {'id': kwargs['id']})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_port_template)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdatePortTemplateService, request.data.dict() | kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_port_template)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(PortTemplateDeleteService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)

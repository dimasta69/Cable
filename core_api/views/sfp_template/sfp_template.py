from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from models_app.models.sfp_template import SfpTemplate
from core_api.services.sfp_template.sfp_template import SfpTemplateService
from core_api.serializers.sfp_temaplte.sfp_template import SfpTemplateSerializer
from core_api.services.sfp_template.update import UpdateSfpTemplateService
from core_api.serializers.sfp_temaplte.update_sfp_template import UpdateSfpTemplateSerializer
from core_api.services.sfp_template.delete import DeleteSfpTemplateService
from core_api.swagger_scheme.sfp_template import sfp_template, update_sfp_template, delete_sfp_template
from utils.services import ServiceOutcome


class SfpTemplateView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = SfpTemplate.objects.all()
    serializer_class = UpdateSfpTemplateSerializer

    @swagger_auto_schema(**sfp_template)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(SfpTemplateService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_sfp_template)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateSfpTemplateService, request.data.dict() | kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_sfp_template)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteSfpTemplateService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateSerializer(outcome.result).data, status=outcome.response_status)

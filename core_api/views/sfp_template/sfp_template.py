from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.services.sfp_template.delete import DeleteSfpTemplateService
from core_api.serializers.sfp_template.sfp_template_list import SfpTemplateListSerializer
from core_api.swagger_scheme.sfp_template import delete_sfp_template


class SfpTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**delete_sfp_template)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteSfpTemplateService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateListSerializer(outcome.result).data, status=outcome.response_status)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.services.sfp_template.delete import DeleteSfpTemplateService
from core_api.serializers.sfp_template.resource import SfpTemplateListSerializer


class SfpTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteSfpTemplateService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateListSerializer(outcome.result).data, status=outcome.response_status)

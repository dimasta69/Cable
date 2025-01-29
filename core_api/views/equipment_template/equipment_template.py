from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.serializers.equipment_template.resource import EquipmentTemplateSerializer
from core_api.services.equipment_template.update import UpdateEquipmentTemplate
from core_api.services.equipment_template.delete import DeleteEquipmentTemplateService


class EquipmentTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateEquipmentTemplate, kwargs | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteEquipmentTemplateService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

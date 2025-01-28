from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.serializers.equipment_template.resource import EquipmentTemplateSerializer
from core_api.services.equipment_template.equipment_template import EquipmentTemplateService
from core_api.services.equipment_template.update import UpdateEquipmentTemplate
from core_api.services.equipment_template.delete import DeleteEquipmentTemplateService
from core_api.swagger_scheme.equipment_template import (equipment_template, update_equipment_template,
                                                        delete_equipment_template)


class EquipmentTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**equipment_template)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(EquipmentTemplateService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_equipment_template)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateEquipmentTemplate, kwargs | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_equipment_template)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteEquipmentTemplateService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

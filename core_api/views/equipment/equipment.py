from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.services.equipment.equipment import EquipmentService
from core_api.serializers.equipment.equipment import EquipmentSerializer
from core_api.services.equipment.delete import DeleteEquipmentService
from core_api.services.equipment.update import UpdateEquipmentService
from core_api.serializers.equipment.update import UpdateEquipmentSerializer
from core_api.serializers.server_rack.server_rack import ServerRackSerializer
from core_api.swagger_scheme.equipment import equipment, delete_equipment, update_equipment


class EquipmentView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateEquipmentSerializer

    @swagger_auto_schema(**equipment)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(EquipmentService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_equipment)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateEquipmentService, request.data | kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_equipment)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteEquipmentService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackSerializer(outcome.result).data, status=outcome.response_status)

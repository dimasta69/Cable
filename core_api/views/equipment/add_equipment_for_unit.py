from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.serializers.equipment.equipment import EquipmentSerializer
from core_api.services.equipment.add_equipment_for_unit import AddEquipmentUnitService
from core_api.swagger_scheme.equipment import add_equipment_for_unit


class AddEquipmentForUnitView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**add_equipment_for_unit)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(AddEquipmentUnitService, request.data
                                 | kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)

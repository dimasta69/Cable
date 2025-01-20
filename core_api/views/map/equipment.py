from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from utils.services import ServiceOutcome
from core_api.serializers.map.equipment.equipment_is_active import EquipmentIsActiveMapSerializer
from core_api.services.map.update_equipment import UpdateEquipmentService


class EquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def path(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            UpdateEquipmentService,
            {"current_user": request.user} | kwargs | request.data
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentIsActiveMapSerializer(outcome.result).data, status=status.HTTP_200_OK)

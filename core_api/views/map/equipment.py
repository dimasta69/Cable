from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core_api.services.map.equipment_list import EquipmentListService
from core_api.services.map.delete import DeleteEquipmentSchemeService
from utils.services import ServiceOutcome
from core_api.serializers.map.equipment.resource import EquipmentIsActiveMapSerializer
from core_api.services.map.update_equipment import UpdateEquipmentService


class EquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            EquipmentListService,
            {"current_user": request.user} | kwargs
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentIsActiveMapSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            UpdateEquipmentService,
            {"current_user": request.user} | kwargs | request.data
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentIsActiveMapSerializer(outcome.result).data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            DeleteEquipmentSchemeService,
            {"current_user": request.user} | kwargs
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(
            {}, status=status.HTTP_204_NO_CONTENT
        )

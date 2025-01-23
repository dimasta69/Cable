from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from utils.services import ServiceOutcome
from core_api.services.map.add_equipment import AddEquipmentMapService
from core_api.services.map.equipment_list import EquipmentListService
from core_api.serializers.map.equipment.equipment_is_active import EquipmentIsActiveMapSerializer


class EquipmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            EquipmentListService,
            {"current_user": request.user} | kwargs
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentIsActiveMapSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK)

    def post(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            AddEquipmentMapService,
            request.data | {"current_user": request.user}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentIsActiveMapSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

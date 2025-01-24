from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from utils.services import ServiceOutcome
from core_api.serializers.map.equipment.equipment_is_active import EquipmentIsActiveMapSerializer
from core_api.services.map.resfresh import RefreshEquipmentMapService


class MapRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, **kwargs):
        outcome: ServiceOutcome = ServiceOutcome(
            RefreshEquipmentMapService,
            {
                "current_user": request.user,
            } | kwargs,
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(
            EquipmentIsActiveMapSerializer(
                outcome.result,
                many=True,
            ).data,
            status=status.HTTP_200_OK,
        )

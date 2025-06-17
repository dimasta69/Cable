from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.services.equipment_type.list import ListEquipmentTypeService
from core_api.serializers.equipment_type.resource import EquipmentTypeSerializer


class ListEquipmentTypeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(ListEquipmentTypeService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTypeSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK)

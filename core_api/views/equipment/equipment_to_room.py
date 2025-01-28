from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from utils.services import ServiceOutcome
from core_api.services.equipment.add_to_room import AddEquipmentFromRoomService
from core_api.serializers.equipment.list import EquipmentListSerializer


class AddEquipmentRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        outcome = ServiceOutcome(AddEquipmentFromRoomService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=status.HTTP_200_OK)

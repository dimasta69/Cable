from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from utils.services import ServiceOutcome
from core_api.services.equipment.create_from_room import CreateEquipmentFromRoomService


class AddEquipmentRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        outcome = ServiceOutcome(CreateEquipmentFromRoomService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_200_OK)

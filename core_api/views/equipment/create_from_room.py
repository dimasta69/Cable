from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from core_api.serializers.equipment.create_from_room import CreateFromRoomEquipmentSerializer
from core_api.services.equipment.create_from_room import CreateEquipmentFromRoomService
from core_api.serializers.equipment.equipment import EquipmentSerializer
from core_api.swagger_scheme.equipment import create_equipment_from_room
from utils.services import ServiceOutcome


class CreateEquipmentFromRoomView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateFromRoomEquipmentSerializer

    @swagger_auto_schema(**create_equipment_from_room)
    def post(self, request):
        outcome = ServiceOutcome(CreateEquipmentFromRoomService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)

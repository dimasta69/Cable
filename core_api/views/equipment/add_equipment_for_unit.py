from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.serializers.server_rack.resource import ServerRackSerializer
from core_api.services.equipment.add_equipment_for_unit import AddEquipmentUnitService


class AddEquipmentForUnitView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(
            AddEquipmentUnitService, request.data | kwargs | {'current_user': request.user}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackSerializer(outcome.result).data, status=outcome.response_status)

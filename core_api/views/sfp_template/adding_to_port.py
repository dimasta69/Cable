from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core_api.services.sfp_template.adding_to_ports import AddToPortSfpService
from core_api.serializers.equipment.resource import EquipmentSerializer
from utils.services import ServiceOutcome


class AddingToPortSfpTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(AddToPortSfpService, request.data | kwargs | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)

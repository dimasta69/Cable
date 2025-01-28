from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from core_api.services.sfp_template.adding_to_ports import AddToPortSfpService
from core_api.serializers.equipment.equipment import EquipmentSerializer
from core_api.swagger_scheme.sfp_template import adding_to_ports
from utils.services import ServiceOutcome


class AddingToPortSfpTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**adding_to_ports)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(AddToPortSfpService, request.data | kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)

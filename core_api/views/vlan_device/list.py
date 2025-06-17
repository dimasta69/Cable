from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from utils.services import ServiceOutcome
from core_api.services.vlan_device.create import CreateVlanDeviceService
from core_api.serializers.vlan.device.resource import VlanDeviceSerializer


class VlanDeviceListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        outcome: ServiceOutcome = ServiceOutcome(
            CreateVlanDeviceService,
            request.data | {"current_user": request.user},
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(VlanDeviceSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_spectacular.utils import extend_schema

from utils.services import ServiceOutcome
from core_api.services.vlan_device.update import UpdateVlanDeviceService
from core_api.services.vlan_device.delete import DeleteVlanDeviceService
from core_api.serializers.vlan.device.resource import VlanDeviceSerializer
from core_api.docs.vlan_device.patch import doc as vlan_device_patch_doc


class VlanDeviceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**vlan_device_patch_doc)
    def patch(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            UpdateVlanDeviceService,
            request.data | {"current_user": request.user} | kwargs,
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(VlanDeviceSerializer(outcome.result).data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        outcome: ServiceOutcome = ServiceOutcome(
            DeleteVlanDeviceService,
            {"current_user": request.user} | kwargs,
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

from rest_framework.views import APIView
from rest_framework import  status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from utils.services import ServiceOutcome
from core_api.services.vlan.delete import DeleteVlanService
from core_api.services.vlan.update import UpdateVlanService
from core_api.serializers.vlan.resource import VlanSerializer


class VlanView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, **kwargs):
        outcome: ServiceOutcome = ServiceOutcome(
            UpdateVlanService,
            request.data | {"current_user": request.user} | kwargs,
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(VlanSerializer(outcome.result).data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            DeleteVlanService,
            {"current_user": request.user} | kwargs,
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

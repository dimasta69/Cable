from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.services.port_mode.list import PortModeListService
from core_api.serializers.port_mode.resource import PortModeSerializer


class PortModeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            PortModeListService,
            dict(request.GET.items()),
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortModeSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK)

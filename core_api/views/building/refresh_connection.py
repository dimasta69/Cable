from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from utils.services import ServiceOutcome
from core_api.services.building.refresh_connection import RefreshBuildingConnectionService


class RefreshBildingsConnectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            RefreshBuildingConnectionService,
            request.data | {"current_user": request.user}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_200_OK)

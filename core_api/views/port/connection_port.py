from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core_api.services.port.connection import ConnectionPortService
from utils.services import ServiceOutcome


class ConnectionPortView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        outcome = ServiceOutcome(ConnectionPortService, request.user | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_200_OK)

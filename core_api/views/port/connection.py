from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from utils.services import ServiceOutcome
from core_api.services.port.connection import ConnectionPortService
from core_api.services.port.disconnect import DisconnectPortService


class ConnectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        outcome = ServiceOutcome(ConnectionPortService, request.data | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_200_OK)


class DisconnectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        outcome = ServiceOutcome(DisconnectPortService, request.data | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.services.port.disconnect_sfp import DisconnectSfpService
from core_api.serializers.port.resource import PortListSerializer
from utils.services import ServiceOutcome


class DisconnectSfpView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        outcome = ServiceOutcome(DisconnectSfpService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

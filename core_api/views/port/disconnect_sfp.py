from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.serializers.port.disconnect_sfp import DisconnectSfpSerializer
from core_api.services.port.disconnect_sfp import DisconnectSfpService
from core_api.serializers.port.port_list import PortListSerializer
from core_api.swagger_scheme.port import disconnect_sfp
from utils.services import ServiceOutcome


class DisconnectSfpView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisconnectSfpSerializer

    @swagger_auto_schema(**disconnect_sfp)
    def put(self, request):
        outcome = ServiceOutcome(DisconnectSfpService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result).data, status=outcome.response_status)

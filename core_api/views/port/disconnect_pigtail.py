from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.serializers.port.disconnect_pigtail import DisconnectPigtail
from core_api.services.port.disconnect_pigtail import DisconnectPigtailService
from core_api.serializers.port.port_list import PortListSerializer
from core_api.swagger_scheme.port import disconnect_pigtail
from utils.services import ServiceOutcome


class DisconnectPigtailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DisconnectPigtail

    @swagger_auto_schema(**disconnect_pigtail)
    def put(self, request):
        outcome = ServiceOutcome(DisconnectPigtailService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

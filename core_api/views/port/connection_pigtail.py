from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.serializers.port.connection_pigtail import ConnectionPigtailSerializer
from core_api.services.port.connection_pigtail import ConnectionPigtailService
from core_api.serializers.port.port_list import PortListSerializer
from core_api.swagger_scheme.port import port_connection_pigtail
from utils.services import ServiceOutcome


class ConnectionPigtailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionPigtailSerializer

    @swagger_auto_schema(**port_connection_pigtail)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(ConnectionPigtailService, kwargs | request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result).data, status=outcome.response_status)
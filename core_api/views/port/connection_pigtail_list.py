from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.serializers.port.connection_pigtail_list import ConnectionPigtailListSerializer
from core_api.services.port.connection_pigtail_list import ConnectionPigtailListService
from core_api.serializers.port.port_list import PortListSerializer
from core_api.swagger_scheme.port import port_connection_pigtail_list
from utils.services import ServiceOutcome


class ConnectionPigtailListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConnectionPigtailListSerializer

    @swagger_auto_schema(**port_connection_pigtail_list)
    def put(self, request):
        outcome = ServiceOutcome(ConnectionPigtailListService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

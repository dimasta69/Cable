from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.serializers.type_port.type_port_list import TypePortListSerializer
from core_api.services.type_port.type_port_list import TypePortListService
from core_api.swagger_scheme.type_port import type_port_list


class TypePortListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**type_port_list)
    def get(self, request):
        outcome = ServiceOutcome(TypePortListService, request)
        return Response(TypePortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

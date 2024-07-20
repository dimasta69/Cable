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
    def post(self, request):
        outcome = ServiceOutcome(TypePortListService)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(TypePortListSerializer(outcome.result).data, status=outcome.response_status)

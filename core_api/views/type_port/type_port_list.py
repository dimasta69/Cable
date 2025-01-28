from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.serializers.type_port.resource import TypePortListSerializer
from core_api.services.type_port.type_port_list import TypePortListService
from core_api.services.type_port.create import CreateTypePort


class TypePortListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(TypePortListService, request)
        return Response(TypePortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateTypePort, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(TypePortListSerializer(outcome.result).data, status=outcome.response_status)

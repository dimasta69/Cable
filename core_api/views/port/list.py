from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.services.port.list import PortListService
from core_api.serializers.port.resource import PortListSerializer


class PortListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        outcome = ServiceOutcome(PortListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

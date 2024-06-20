from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from models_app.models.port import Port
from core_api.services.port.port_list import PortListService


class PortView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Port.objects.all()

    @swagger_auto_schema()
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(PortListService, request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)
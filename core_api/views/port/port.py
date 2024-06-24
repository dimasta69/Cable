from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from models_app.models.port import Port
from core_api.serializers.port.update import UpdatePortSerializer
from core_api.services.port.update import UpdatePortService
from core_api.serializers.port.port_list import PortListSerializer
from core_api.swagger_scheme.port import update_port
from utils.services import ServiceOutcome


class PortView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Port.objects.all()
    serializer_class = UpdatePortSerializer

    @swagger_auto_schema(**update_port)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdatePortService, kwargs | request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result).data, status=outcome.response_status)

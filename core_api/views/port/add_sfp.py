from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.services.port.add_sfp import AddSfpService
from core_api.serializers.port.port_list import PortListSerializer
from core_api.swagger_scheme.port import add_sfp
from utils.services import ServiceOutcome


class AddSfpView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**add_sfp)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(AddSfpService, kwargs | request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

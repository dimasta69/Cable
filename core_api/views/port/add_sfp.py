from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.services.port.add_sfp import AddSfpService
from core_api.serializers.port.resource import PortListSerializer
from utils.services import ServiceOutcome


class AddSfpView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(AddSfpService, kwargs | request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortListSerializer(outcome.result, many=True).data, status=outcome.response_status)

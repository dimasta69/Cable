from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.services.server_rack.server_rack import ServerRackService
from core_api.services.server_rack.delete import DeleteServerRackService
from core_api.services.server_rack.update import UpdateServerRackService
from core_api.serializers.server_rack.list import ServerRackListSerializer
from core_api.serializers.server_rack.resource import ServerRackSerializer


class ServerRackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        outcome = ServiceOutcome(ServerRackService, kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackSerializer(outcome.result).data, status=outcome.response_status)

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateServerRackService, request.data | kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackListSerializer(outcome.result).data, status=outcome.response_status)

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteServerRackService, kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackListSerializer(outcome.result).data, status=outcome.response_status)

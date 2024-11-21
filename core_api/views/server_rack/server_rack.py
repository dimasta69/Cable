from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.services.server_rack.server_rack import ServerRackService
from core_api.services.server_rack.delete import DeleteServerRackService
from core_api.services.server_rack.update import UpdateServerRackService
from core_api.serializers.server_rack.server_rack_list import ServerRackListSerializer
from core_api.serializers.server_rack.update import UpdateServerRackSerializer
from core_api.serializers.server_rack.server_rack import ServerRackSerializer
from core_api.swagger_scheme.server_rack import server_rack, delete_server_rack, update_server_rack


class ServerRackView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateServerRackSerializer

    @swagger_auto_schema(**server_rack)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(ServerRackService, kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_server_rack)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateServerRackService, request.data | kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_server_rack)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteServerRackService, kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackListSerializer(outcome.result).data, status=outcome.response_status)

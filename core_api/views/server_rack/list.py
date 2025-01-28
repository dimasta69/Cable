from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.serializers.server_rack.list import ServerRackListSerializer
from core_api.services.server_rack.rack_list import ServerRackListService
from core_api.services.server_rack.create import CreateServerRackService
from core_api.swagger_scheme.server_rack import server_rack_list, create_server_rack


class ServerRackListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**server_rack_list)
    def get(self, request):
        outcome = ServiceOutcome(ServerRackListService, dict(request.GET.items()) | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors)
        return Response(ServerRackListSerializer(outcome.result, many=True).data, status=outcome.response_status)

    @swagger_auto_schema(**create_server_rack)
    def post(self, request):
        outcome = ServiceOutcome(CreateServerRackService, request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackListSerializer(outcome.result).data, status=outcome.response_status)

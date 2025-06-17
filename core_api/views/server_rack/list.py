from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from utils.services import ServiceOutcome
from core_api.serializers.server_rack.list import ServerRackListSerializer
from core_api.services.server_rack.rack_list import ServerRackListService
from core_api.services.server_rack.create import CreateServerRackService


class ServerRackListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(ServerRackListService, dict(request.GET.items()) | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors)
        return Response(ServerRackListSerializer(outcome.result, many=True).data, status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateServerRackService, request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ServerRackListSerializer(outcome.result).data, status=outcome.response_status)

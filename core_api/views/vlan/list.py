from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core_api.services.vlan.create import CreateVlanService
from core_api.services.vlan.list import VlanListService
from core_api.serializers.vlan.resource import VlanSerializer
from utils.services import ServiceOutcome



class VlanListView(APIView)
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            VlanListService,
            dict(request.GET.items()) | {"current_user": request.user},
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(VlanSerializer(outcome.result).data, status=status.HTTP_200_OK)
    def post(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            CreateVlanService,
            request.data | {"current_user": request.user},
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(VlanSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

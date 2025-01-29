from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.serializers.building.resource import BuildingListSerializer
from core_api.services.building.update import UpdateBuildingService
from core_api.services.building.delete import DeleteBuildingService


class BuildingView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateBuildingService, request.data | kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(BuildingListSerializer(outcome.result).data, status=outcome.response_status)

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteBuildingService, kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(BuildingListSerializer(outcome.result).data, status=outcome.response_status)

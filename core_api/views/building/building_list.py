from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from models_app.models.building import Building
from core_api.serializers.building.building_list import BuildingListSerializer
from core_api.services.building.building_list import BuildingListService
from core_api.services.building.create import CreateBuildingService
from core_api.serializers.building.create import CreateBuildingSerializer
from core_api.swagger_scheme.building import building_list, create_building


class BuildingListView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Building.objects.all()
    serializer_class = CreateBuildingSerializer

    @swagger_auto_schema(**building_list)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(BuildingListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(BuildingListSerializer(outcome.result, many=True).data, status=outcome.response_status)

    @swagger_auto_schema(**create_building)
    def post(self, request, **kwargs):
        outcome = ServiceOutcome(CreateBuildingService, request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(BuildingListSerializer(outcome.result).data, status=outcome.response_status)

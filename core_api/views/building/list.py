from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.pagination import CustomPagination

from utils.services import ServiceOutcome
from core_api.serializers.building.resource import BuildingListSerializer
from core_api.services.building.list import BuildingListService
from core_api.services.building.create import CreateBuildingService


class BuildingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(BuildingListService, dict(request.GET.items()) | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': BuildingListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateBuildingService, request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(BuildingListSerializer(outcome.result).data, status=outcome.response_status)

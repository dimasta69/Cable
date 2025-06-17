from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from core_api.services.map.create import CreateMapService
from utils.services import ServiceOutcome
from core_api.services.map.list import MapListService
from core_api.serializers.map.resourse import MapSerializer


class MapListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(
            MapListService,
            dict(request.GET.items()) | {"current_user": request.user}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(MapSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        outcome = ServiceOutcome(CreateMapService, {"current_user": request.user} | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(MapSerializer(outcome.result).data, status=status.HTTP_201_CREATED)
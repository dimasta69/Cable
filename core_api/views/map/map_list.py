from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.services.map.map_list import MapListService
from core_api.serializers.map.map_list import MapListSerializer


class MapListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(
            MapListService,
            dict(request.GET.items()) | {"current_user": request.user}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(MapListSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK)

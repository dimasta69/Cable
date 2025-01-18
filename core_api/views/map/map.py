from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core_api.services.map.create import CreateMapService
from core_api.serializers.map.resourse import MapSerializer
from utils.services import ServiceOutcome


class MapView(APIView):
    permission_classes = [IsAuthenticated]

    # def post(self, request):
    #     outcome = ServiceOutcome(CreateMapService, {"current_user": request.user} | request.data)
    #     if bool(outcome.errors):
    #         return Response(outcome.errors, status=outcome.response_status)
    #     return Response(MapSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.serializers.room.room_list import RoomListSerializer
from core_api.serializers.room.create import CreateRoomSerializer
from core_api.services.room.room_list import RoomListService
from core_api.services.room.create import CreateRoomService
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class RoomListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateRoomSerializer

    # @swagger_auto_schema(**)
    def get(self, request):
        outcome = ServiceOutcome(RoomListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': RoomListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    # @swagger_auto_schema(**)
    def post(self, request):
        outcome = ServiceOutcome(CreateRoomService, request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(CreateRoomSerializer(outcome.result).data, status=outcome.response_status)

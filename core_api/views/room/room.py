from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.services.room.delete import DeleteRoomService
from core_api.services.room.update import UpdateRoomService
from core_api.serializers.room.room_list import RoomListSerializer
from core_api.serializers.room.update import UpdateRoomSerializer
from core_api.swagger_scheme.room import delete_room, update_room


class RoomView(APIView):
    serializer_class = UpdateRoomSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**update_room)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateRoomService, request.data | kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(RoomListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_room)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteRoomService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(RoomListSerializer(outcome.result).data, status=outcome.response_status)

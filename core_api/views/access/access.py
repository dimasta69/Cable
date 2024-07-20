from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.services.access.delete import DeleteAccessService
from core_api.serializers.access.access_list import AccessListSerializer
from core_api.swagger_scheme.access import delete_room, update_access
from core_api.serializers.access.update import UpdateAccessSerializer
from core_api.services.access.update import UpdateAccessService


class AccessView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateAccessSerializer

    @swagger_auto_schema(**update_access)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateAccessService, request.data | kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_room)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteAccessService, kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result).data, status=outcome.response_status)

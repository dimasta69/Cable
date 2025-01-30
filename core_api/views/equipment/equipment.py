from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.services.equipment.equipment import EquipmentService
from core_api.serializers.equipment.list import EquipmentListSerializer
from core_api.serializers.equipment.resource import EquipmentSerializer
from core_api.services.equipment.delete import DeleteEquipmentService
from core_api.services.equipment.update import UpdateEquipmentService
from core_api.services.equipment.release_equipment import ReleaseEquipmentService


class EquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        outcome = ServiceOutcome(EquipmentService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=outcome.response_status)

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateEquipmentService, request.data | kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteEquipmentService, kwargs | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentSerializer(outcome.result).data, status=outcome.response_status)


class ReleaseEquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, **kwargs):
        outcome = ServiceOutcome(ReleaseEquipmentService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=status.HTTP_200_OK)

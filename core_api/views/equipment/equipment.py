from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from utils.services import ServiceOutcome
from core_api.services.equipment.equipment import EquipmentService
from core_api.serializers.equipment.list import EquipmentListSerializer
from core_api.services.equipment.delete import DeleteEquipmentService
from core_api.services.equipment.update import UpdateEquipmentService
from core_api.services.equipment.release_equipment import ReleaseEquipmentService

from core_api.docs.equipment.get_detail import doc as equipment_get_detail_doc
from core_api.docs.equipment.put import doc as equipment_put_doc
from core_api.docs.equipment.delete import doc as equipment_delete_doc
from core_api.docs.equipment.patch_release import doc as equipment_patch_release_doc


class EquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**equipment_get_detail_doc)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(EquipmentService, kwargs | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=outcome.response_status)

    @extend_schema(**equipment_put_doc)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateEquipmentService, request.data | kwargs | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=outcome.response_status)

    @extend_schema(**equipment_delete_doc)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteEquipmentService, kwargs | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=outcome.response_status)


class ReleaseEquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**equipment_patch_release_doc)
    def patch(self, request, **kwargs):
        outcome = ServiceOutcome(ReleaseEquipmentService, kwargs | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=status.HTTP_200_OK)

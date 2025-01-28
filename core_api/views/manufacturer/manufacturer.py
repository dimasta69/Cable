from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core_api.serializers.manufacturer.manufacturer_list import ManufacturerListSerializer
from core_api.services.manufacturer.manufacturer import ManufacturerService
from core_api.services.manufacturer.delete import ManufacturerDeleteService
from core_api.services.manufacturer.update import ManufacturerUpdateService
from utils.services import ServiceOutcome


class ManufacturerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        outcome = ServiceOutcome(ManufacturerService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ManufacturerListSerializer(outcome.result).data, status=outcome.response_status)

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(ManufacturerDeleteService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ManufacturerListSerializer(outcome.result).data, status=outcome.response_status)

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(ManufacturerUpdateService, kwargs | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ManufacturerListSerializer(outcome.result).data, status=outcome.response_status)

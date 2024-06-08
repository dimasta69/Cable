from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from models_app.models.manufacturer import Manufacturer
from core_api.serializers.manufacturer.manufacturer_list import ManufacturerListSerializer
from core_api.services.manufacturer.manufacturer import ManufacturerService
from core_api.services.manufacturer.delete import ManufacturerDeleteService
from core_api.services.manufacturer.update import ManufacturerUpdateService
from core_api.swagger_scheme.manufacturer import manufacturer, update_manufacturer, delete_manufacturer
from utils.services import ServiceOutcome


class ManufacturerView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerListSerializer

    @swagger_auto_schema(**manufacturer)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(ManufacturerService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ManufacturerListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_manufacturer)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(ManufacturerDeleteService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ManufacturerListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_manufacturer)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(ManufacturerUpdateService, kwargs | request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ManufacturerListSerializer(outcome.result).data, status=outcome.response_status)

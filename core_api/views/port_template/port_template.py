from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from utils.services import ServiceOutcome
from core_api.services.port_template.port_template import PortTemplateService
from core_api.serializers.port_template.resource import PortTemplateListSerializer
from core_api.services.port_template.update import UpdatePortTemplateService
from core_api.services.port_template.connection_port_ship import ConnectionPortShipService
from core_api.services.port_template.delete import PortTemplateDeleteService
from core_api.swagger_scheme.port_template import port_temple, update_port_template, delete_port_template
from core_api.serializers.port_ship.resource import PortShipSerializer
from core_api.services.port_template.port_ship_list import PortShipListService


class PortTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**port_temple)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(PortTemplateService, {'id': kwargs['id']})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_port_template)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdatePortTemplateService, request.data | kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_port_template)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(PortTemplateDeleteService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)


class PortShipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        outcome = ServiceOutcome(PortShipListService, kwargs)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortShipSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK)


class ConnectionPortShipView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        outcome = ServiceOutcome(ConnectionPortShipService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortShipSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

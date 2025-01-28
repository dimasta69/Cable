from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.serializers.equipment_template.resource import EquipmentTemplateSerializer
from core_api.services.equipment_template.list import EquipmentTemplateListService
from core_api.services.equipment_template.create import CreateEquipmentTemplateService
from core_api.swagger_scheme.equipment_template import equipment_template_list, create_equipment_template
from utils.services import ServiceOutcome


class EquipmentTemplateListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**equipment_template_list)
    def get(self, request):
        if "filter_speed" in dict(request.GET.items()):
            filter_speed = json.loads(dict(request.GET.items())['filter_speed'])
        else:
            filter_speed = None
        if "filter_line_type" in dict(request.GET.items()):
            filter_line_type = json.loads(dict(request.GET.items())['filter_line_type'])
        else:
            filter_line_type = None
        outcome = ServiceOutcome(EquipmentTemplateListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result, many=True).data, status=outcome.response_status)

    @swagger_auto_schema(**create_equipment_template)
    def post(self, request):
        outcome = ServiceOutcome(CreateEquipmentTemplateService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

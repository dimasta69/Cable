import json

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.pagination import CustomPagination

from core_api.serializers.equipment_template.resource import EquipmentTemplateSerializer
from core_api.services.equipment_template.list import EquipmentTemplateListService
from core_api.services.equipment_template.create import CreateEquipmentTemplateService
from utils.services import ServiceOutcome


class EquipmentTemplateListView(APIView):
    permission_classes = [IsAuthenticated]

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
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': EquipmentTemplateSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateEquipmentTemplateService, request.data | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

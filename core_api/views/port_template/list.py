import json
from rest_framework.views import APIView
from rest_framework.response import Response

from core_api.serializers.port_template.resource import PortTemplateListSerializer
from core_api.services.port_template.port_template_list import PortTemplateListService
from core_api.services.port_template.create import CreatePortTemplateService
from rest_framework.permissions import IsAuthenticated
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class PortTemplateListView(APIView):
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
        outcome = ServiceOutcome(
            PortTemplateListService,
            dict(request.GET.items()) |
            {
                "filter_speed": filter_speed,
                "filter_line_type": filter_line_type,
            }
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': PortTemplateListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreatePortTemplateService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(PortTemplateListSerializer(outcome.result).data, status=outcome.response_status)

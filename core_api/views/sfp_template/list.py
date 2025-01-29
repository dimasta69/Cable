from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core_api.serializers.sfp_template.resource import SfpTemplateListSerializer
from core_api.services.sfp_template.list import SfpTemplateListService
from core_api.services.sfp_template.create import CreateSfpTemplateService
from utils.pagination import CustomPagination
from utils.services import ServiceOutcome


class SfpTemplateListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(SfpTemplateListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': SfpTemplateListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateSfpTemplateService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateListSerializer(outcome.result).data, status=outcome.response_status)

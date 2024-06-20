from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from models_app.models.sfp_template import SfpTemplate
from core_api.services.sfp_template.sfp_template_list import SfpTemplateListService
from core_api.serializers.sfp_temaplte.sfp_template import SfpTemplateSerializer
from core_api.services.sfp_template.create import CreateSfpTemplateService
from core_api.serializers.sfp_temaplte.create_sfp_template import CreateSfpTemplateSerializer
from core_api.swagger_scheme.sfp_template import sfp_template_list, create_sfp_template
from rest_framework.permissions import IsAuthenticated
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class SfpTemplateListView(APIView):
    serializer_class = CreateSfpTemplateSerializer
    queryset = SfpTemplate.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**sfp_template_list)
    def get(self, request):
        outcome = ServiceOutcome(SfpTemplateListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': SfpTemplateSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    @swagger_auto_schema(**create_sfp_template)
    def post(self, request):
        outcome = ServiceOutcome(CreateSfpTemplateService, request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateSerializer(outcome.result).data, status=outcome.response_status)


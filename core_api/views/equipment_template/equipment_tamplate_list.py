from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from models_app.models.equipment.equipment_template.models import EquipmentTemplate
from core_api.serializers.equipment_template.equipment_template_list import EquipmentTemplateListSerializer
from core_api.serializers.equipment_template.equipment_template import EquipmentTemplateSerializer
from core_api.serializers.equipment_template.create_equipment_template import CreateEquipmentTemplateSerializer
from core_api.services.equipment_template.equipment_template_list import EquipmentTemplateListService
from core_api.services.equipment_template.create import CreateEquipmentTemplateService
from core_api.swagger_scheme.equipment_template import equipment_template_list, create_equipment_template
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class EquipmentTemplateListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateEquipmentTemplateSerializer
    queryset = EquipmentTemplate.objects.all()

    @swagger_auto_schema(**equipment_template_list)
    def get(self, request):
        outcome = ServiceOutcome(EquipmentTemplateListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': EquipmentTemplateListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    @swagger_auto_schema(**create_equipment_template)
    def post(self, request):
        outcome = ServiceOutcome(CreateEquipmentTemplateService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentTemplateSerializer(outcome.result).data, status=outcome.response_status)

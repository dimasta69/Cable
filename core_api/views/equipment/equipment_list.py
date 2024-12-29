from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from models_app.models import Equipment
from core_api.serializers.equipment.create import CreateEquipmentSerializer
from core_api.services.equipment.create import CreateEquipmentService
from core_api.services.equipment.equipment_list import EquipmentListService
from core_api.serializers.equipment.equipment_list import EquipmentListSerializer
from core_api.swagger_scheme.equipment import create_equipment, equipment_list
from utils.pagination import CustomPagination
from utils.services import ServiceOutcome


class EquipmentListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateEquipmentSerializer
    queryset = Equipment.objects.all()

    @swagger_auto_schema(**equipment_list)
    def get(self, request):
        outcome = ServiceOutcome(EquipmentListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': EquipmentListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    @swagger_auto_schema(**create_equipment)
    def post(self, request):
        outcome = ServiceOutcome(CreateEquipmentService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(EquipmentListSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

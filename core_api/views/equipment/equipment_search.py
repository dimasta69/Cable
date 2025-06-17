import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from utils.pagination import CustomPagination
from core_api.services.equipment.equipment_from_search import EquipmentFromSearchService
from core_api.serializers.equipment.list import EquipmentListSerializer


class EquipmentSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        if "filter_vlan_list_id" in dict(request.GET.items()):
            filter_vlan_list_id = json.loads(dict(request.GET.items())['filter_vlan_list_id'])
        else:
            filter_vlan_list_id = None
        outcome = ServiceOutcome(
            EquipmentFromSearchService,
            {
                "current_user": request.user,
                "filter_vlan_list_id": filter_vlan_list_id
            } | kwargs | dict(request.GET.items())
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': EquipmentListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)
    
from rest_framework.views import APIView
from rest_framework.response import Response

from core_api.services.manufacturer.manufacturer_list import ManufacturerListService
from core_api.services.manufacturer.create import CreateManufactureService
from core_api.serializers.manufacturer.resource import ManufacturerListSerializer

from rest_framework.permissions import IsAuthenticated
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class ManufacturerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(ManufacturerListService, dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': ManufacturerListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateManufactureService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(ManufacturerListSerializer(outcome.result).data, status=outcome.response_status)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from core_api.services.access.access_list import AccessListService
from core_api.serializers.access.access_list import AccessListSerializer
from core_api.serializers.access.create import CreateAccessSerializer
from core_api.services.access.create import CreateAccessService
from core_api.swagger_scheme.access import access_list, create_access
from utils.services import ServiceOutcome
from utils.pagination import CustomPagination


class AccessListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateAccessSerializer

    @swagger_auto_schema(**access_list)
    def get(self, request):
        outcome = ServiceOutcome(AccessListService, dict(request.GET.items()) | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': AccessListSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    @swagger_auto_schema(**create_access)
    def post(self, request):
        outcome = ServiceOutcome(CreateAccessService, request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result).data, status=outcome.response_status)

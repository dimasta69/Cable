from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from core_api.services.scheme.list import SchemeListService
from core_api.services.scheme.create import CreateScheme
from core_api.serializers.scheme.resource import SchemeSerializer
from utils.services import ServiceOutcome


class SchemeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(SchemeListService, {'current_user': request.user} | dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors)
        return Response(SchemeSerializer(outcome.result, many=True).data, status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateScheme, {'current_user': request.user} | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

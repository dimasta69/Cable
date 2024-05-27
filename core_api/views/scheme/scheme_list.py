from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from models_app.models.scheme import Scheme
from core_api.services.scheme.scheme_list import SchemeListService
from core_api.services.scheme.create import CreateScheme
from core_api.serializers.scheme.scheme_list import SchemeSerializer
from core_api.swagger_scheme.scheme import scheme_list, create_scheme
from utils.services import ServiceOutcome


class SchemeListView(APIView):
    queryset = Scheme.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SchemeSerializer

    @swagger_auto_schema(**scheme_list)
    def get(self, request):
        outcome = ServiceOutcome(SchemeListService, {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors)
        return Response(SchemeSerializer(outcome.result, many=True).data, status=outcome.response_status)

    @swagger_auto_schema(**create_scheme)
    def post(self, request):
        outcome = ServiceOutcome(CreateScheme, {'current_user': request.user} | request.data.dict())
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from models_app.models import Scheme
from core_api.serializers.scheme.scheme_list import SchemeSerializer
from core_api.services.scheme.scheme import SchemeService
from core_api.services.scheme.delete import SchemeDeleteService
from core_api.services.scheme.update import SchemeUpdateService
from core_api.swagger_scheme.scheme import delete_scheme
from core_api.swagger_scheme.scheme import update_scheme
from utils.services import ServiceOutcome
from core_api.swagger_scheme.scheme import scheme


class SchemeView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Scheme.objects.all()
    serializer_class = SchemeSerializer

    @swagger_auto_schema(**scheme)
    def get(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeService, {'current_user': request.user, 'id': kwargs['id']})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**delete_scheme)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeDeleteService, {'current_user': request.user,
                                                       'id': kwargs['id']})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

    @swagger_auto_schema(**update_scheme)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeUpdateService, {'current_user': request.user, 'id': kwargs['id']} | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core_api.serializers.scheme.resource import SchemeSerializer
from core_api.services.scheme.scheme import SchemeService
from core_api.services.scheme.delete import SchemeDeleteService
from core_api.services.scheme.update import SchemeUpdateService
from utils.services import ServiceOutcome


class SchemeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeService, {'current_user': request.user, 'id': kwargs['id']})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeDeleteService, {'current_user': request.user,
                                                       'id': kwargs['id']})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

    def put(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeUpdateService, {'current_user': request.user, 'id': kwargs['id']} | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core_api.serializers.scheme.resource import SchemeSerializer
from core_api.services.scheme.delete import SchemeDeleteService
from core_api.services.scheme.update import SchemeUpdateService
from utils.services import ServiceOutcome

from core_api.docs.scheme.delete import doc as scheme_delete_doc
from core_api.docs.scheme.put import doc as scheme_put_doc


class SchemeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**scheme_delete_doc)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeDeleteService, {'current_user': request.user,
                                                       'id': kwargs['id']})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

    @extend_schema(**scheme_put_doc)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(SchemeUpdateService, {'current_user': request.user, 'id': kwargs['id']} | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

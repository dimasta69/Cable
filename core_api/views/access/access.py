from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from utils.services import ServiceOutcome
from core_api.services.access.delete import DeleteAccessService
from core_api.serializers.access.resource import AccessListSerializer
from core_api.services.access.update import UpdateAccessService

from core_api.docs.access.put import doc as access_put_docs
from core_api.docs.access.delete import doc as access_delete_docs


class AccessView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**access_put_docs)
    def put(self, request, **kwargs):
        outcome = ServiceOutcome(UpdateAccessService, request.data | kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result).data, status=outcome.response_status)

    @extend_schema(**access_delete_docs)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteAccessService, kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result).data, status=outcome.response_status)

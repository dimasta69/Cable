from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from core_api.services.access.scheme_list import AccessListService
from core_api.serializers.access.resource import AccessListSerializer
from core_api.services.access.create_to_scheme import CreateAccessService
from core_api.services.access.list import AccessListService as AccessMoreService
from core_api.services.access.create import CreateAccessService as CreateAccessMoreService
from utils.services import ServiceOutcome

from core_api.docs.access.get import doc as access_get_doc
from core_api.docs.access.post import doc as access_post_doc


class AccessListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**access_get_doc)
    def get(self, request):
        outcome = ServiceOutcome(AccessListService, dict(request.GET.items()) | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result, many=True).data, status=outcome.response_status)

    @extend_schema(**access_post_doc)
    def post(self, request):
        outcome = ServiceOutcome(CreateAccessService, request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result).data, status=outcome.response_status)


class AccessMoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(AccessMoreService, dict(request.GET.items()) | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result, many=True).data, status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(CreateAccessMoreService, request.data | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(AccessListSerializer(outcome.result).data, status=outcome.response_status)
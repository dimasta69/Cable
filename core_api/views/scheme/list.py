from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from utils.pagination import CustomPagination

from core_api.services.scheme.list import SchemeListService
from core_api.services.scheme.create import CreateScheme
from core_api.serializers.scheme.resource import SchemeSerializer
from utils.services import ServiceOutcome

from core_api.docs.scheme.get import doc as scheme_get_doc
from core_api.docs.scheme.post import doc as scheme_post_doc


class SchemeListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**scheme_get_doc)
    def get(self, request):
        outcome = ServiceOutcome(SchemeListService, {'current_user': request.user} | dict(request.GET.items()))
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({'pagination': CustomPagination(outcome.result,
                                                        current_page=outcome.service.cleaned_data['page'],
                                                        per_page=outcome.service.cleaned_data['per_page']).to_json(),
                         'results': SchemeSerializer(outcome.result, many=True).data},
                        status=outcome.response_status)

    @extend_schema(**scheme_post_doc)
    def post(self, request):
        outcome = ServiceOutcome(CreateScheme, {'current_user': request.user} | request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

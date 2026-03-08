from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from utils.services import ServiceOutcome
from core_api.services.sfp_template.delete import DeleteSfpTemplateService
from core_api.services.sfp_template.update import UpdateSfpTemplateService
from core_api.serializers.sfp_template.resource import SfpTemplateListSerializer
from core_api.docs.sfp_template.patch import doc as sfp_template_patch_doc
from core_api.docs.sfp_template.delete import doc as sfp_template_delete_doc


class SfpTemplateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**sfp_template_patch_doc)
    def patch(self, request, **kwargs):
        outcome = ServiceOutcome(
            UpdateSfpTemplateService,
            kwargs | dict(request.data) | {"current_user": request.user},
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateListSerializer(outcome.result).data, status=outcome.response_status)

    @extend_schema(**sfp_template_delete_doc)
    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(DeleteSfpTemplateService, kwargs | {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(SfpTemplateListSerializer(outcome.result).data, status=outcome.response_status)

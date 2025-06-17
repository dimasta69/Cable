from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.serializers.segment.resource import SegmentSerializer
from core_api.services.segment.list import SegmentListService
from core_api.services.segment.create import CreateSegmentService


class SegmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            SegmentListService,
            dict(request.GET.items()) | {"current_user": request.user}
        )
        if bool(outcome.errors):
            return Response(
                outcome.errors, status=outcome.response_status,
            )
        return Response(
            SegmentSerializer(outcome.result, many=True).data, status=status.HTTP_200_OK,
        )

    def post(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            CreateSegmentService,
            request.data | {"current_user": request.user},
        )
        if bool(outcome.errors):
            return Response(
                outcome.errors, status=outcome.response_status,
            )
        return Response(
            SegmentSerializer(outcome.result).data, status=status.HTTP_201_CREATED,
        )

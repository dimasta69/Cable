from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from utils.services import ServiceOutcome
from core_api.serializers.segment.resource import SegmentSerializer
from core_api.services.segment.update import UpdateSegmentService

class SegmentView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            UpdateSegmentService,
            request.data,
        )
        if bool(outcome.errors):
            return Response(
                outcome.errors, status=outcome.response_status
            )
        return Response(
            SegmentSerializer(outcome.result).data, status=status.HTTP_200_OK
        )

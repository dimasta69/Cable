from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.serializers.figure.resource import FigureSerializer
from core_api.services.figure.update import UpdateFigureService
from core_api.services.figure.delete import DeleteFigureService


class UpdateFigureView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            UpdateFigureService,
            request.data | {"current_user": request.user} | kwargs
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(FigureSerializer(outcome.result).data, status=status.HTTP_200_OK)

    def delete(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            DeleteFigureService,
            {"current_user": request.user} | kwargs,
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

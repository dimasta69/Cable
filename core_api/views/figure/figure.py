import django.urls
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.serializers.figure.resource import FigureSerializer
from core_api.services.figure.update import UpdateFigureService


class UpdateFigureView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            UpdateFigureService,
            request.data | {"current_user": request.user} | kwargs
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(FigureSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

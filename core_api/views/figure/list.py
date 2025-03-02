from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.services import ServiceOutcome
from core_api.services.figure.create import CreateFigureService
from core_api.serializers.figure.resource import FigureSerializer
from core_api.services.figure.list import FigureListService


class FigureListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            FigureListService,
            dict(request.GET.items()) | {"current_user": request.user}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(FigureSerializer(outcome.result, many=True).data, status=status.HTTP_201_CREATED)

    def post(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            CreateFigureService,
            request.data | {"current_user": request.user}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(FigureSerializer(outcome.result).data, status=status.HTTP_201_CREATED)

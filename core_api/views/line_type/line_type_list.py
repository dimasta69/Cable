from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from core_api.serializers.line_type.resource import LineTypeSerializer
from models_app.models import LineType


class LineTypeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(LineTypeSerializer(LineType.objects.all(), many=True).data, status=status.HTTP_200_OK)

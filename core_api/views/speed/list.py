from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from models_app.models import Speed
from core_api.serializers.speed.resource import SpeedListSerializer


class SpeedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            SpeedListSerializer(Speed.objects.all().order_by("value"), many=True).data, status=status.HTTP_200_OK
        )

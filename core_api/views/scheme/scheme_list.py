from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from models_app.models.scheme import Scheme
from core_api.services.scheme.scheme_list import SchemeListService
from core_api.serializers.scheme.scheme_list import SchemeSerializer
from utils.services import ServiceOutcome


class SchemeListView(APIView):
    queryset = Scheme.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(SchemeListService, {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors)
        return Response(SchemeSerializer(outcome.result).data, status=outcome.response_status)

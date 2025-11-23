from rest_framework.response import Response
from rest_framework.views import APIView

from license_api.services.mac.mac import MacService
from utils.services import ServiceOutcome


class MacView(APIView):

    def get(self, request):
        outcome = ServiceOutcome(MacService, request.data)
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(outcome.result, status=outcome.response_status)

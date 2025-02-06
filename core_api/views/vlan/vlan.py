from rest_framework.views import APIView
from rest_framework import  status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from utils.services import ServiceOutcome
from core_api.services.vlan.delete import DeleteVlanService



class VlanView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs) -> Response:
        outcome: ServiceOutcome = ServiceOutcome(
            DeleteVlanService,
            {"current_user": request.user} | kwargs,
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

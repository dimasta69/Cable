from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from utils.services import ServiceOutcome


class AccessListView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs):
        outcome = ServiceOutcome(AccessListService, dict(request.GET.items()) | kwargs | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

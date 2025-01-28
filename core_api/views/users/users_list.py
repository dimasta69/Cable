from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.services import ServiceOutcome
from core_api.serializers.users.users_list import UsersListSerializers
from core_api.services.user.users_list import UsersListServices


class UsersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(UsersListServices, dict(request.GET.items()) | {'current_user': request.user})
        return Response(UsersListSerializers(outcome.result, many=True).data, status=outcome.response_status)

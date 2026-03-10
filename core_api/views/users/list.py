from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.pagination import CustomPagination
from utils.services import ServiceOutcome

from core_api.serializers.users.resource import UsersListSerializers
from core_api.services.user.list import UsersListServices


class UsersListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(exclude=True)
    def get(self, request):
        outcome = ServiceOutcome(UsersListServices, dict(request.GET.items()) | {'current_user': request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(
            {
                "pagination": CustomPagination(
                    outcome.result,
                    current_page=outcome.service.cleaned_data["page"],
                    per_page=outcome.service.cleaned_data["per_page"],
                ).to_json(),
                "results": UsersListSerializers(outcome.result, many=True).data,
            },
            status=outcome.response_status,
        )

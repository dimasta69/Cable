from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from license_api.services.license.upload_file import UploadFileService
from utils.services import ServiceOutcome


class LicenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        outcome = ServiceOutcome(
            UploadFileService, {
                "current_user": request.user},
            {"uploaded_file": request.FILES.get('uploaded_file')}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=outcome.response_status)

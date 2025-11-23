from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from license_api.services.license.upload_file import UploadFileService
from license_api.services.license.license import CheckLicenseService
from license_api.serializers.license.check_license import CheckLicenseSerializer
from utils.services import ServiceOutcome


class LicenseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outcome = ServiceOutcome(CheckLicenseService, {"current_user": request.user})
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response(CheckLicenseSerializer(outcome.result).data, status=outcome.response_status)

    def post(self, request):
        outcome = ServiceOutcome(
            UploadFileService, {
                "current_user": request.user},
            {"uploaded_file": request.FILES.get('uploaded_file')}
        )
        if bool(outcome.errors):
            return Response(outcome.errors, status=outcome.response_status)
        return Response({}, status=outcome.response_status)

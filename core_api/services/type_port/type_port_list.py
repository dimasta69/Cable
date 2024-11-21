from rest_framework import status

from models_app.models.type_port import TypePort
from utils.services import ServiceWithResult


class TypePortListService(ServiceWithResult):
    def process(self):
        self.result = TypePort.objects.all() or TypePort.objects.none()
        self.response_status = status.HTTP_200_OK
        return self

from django.core.exceptions import ObjectDoesNotExist, SuspiciousOperation
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from utils.fields import ListIntegerField
from models_app.models.port import Port


class DisconnectSfpService(ServiceWithResult):
    port_list = ListIntegerField(required=True)

    custom_validations = ['port_presence', 'port_already']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.disconnect_sfp
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def disconnect_sfp(self):
        for port in self.port_list_dict:
            port.sfp = None
            port.save()
        return None

    @property
    @lru_cache()
    def port_list_int(self):
        try:
            return Port.objects.all()
        except Port.DoesNotExist:
            return Port.objects.none()

    @property
    @lru_cache()
    def port_list_dict(self):
        port_list_dict = []
        for uid in self.cleaned_data['port_list']:
            try:
                port_list_dict.append(self.port_list_int.get(id=uid))
            except Port.DoesNotExist:
                return None
        return port_list_dict

    def port_presence(self):
        if self.cleaned_data['port_list']:
            if not self.port_list_dict:
                self.add_error('port_list_dict', ObjectDoesNotExist('Port list does not exist'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def port_already(self):
        if self.port_list_dict:
            port_list = [port for port in self.port_list_dict if port.connection is not None]
            if port_list:
                self.add_error('pigtail_list',  SuspiciousOperation('Port is already connected'))
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.server_rack import ServerRack
from models_app.models.unit import Unit


class DeleteServerRackService(ServiceWithResult):
    id = forms.IntegerField(required=True)

    custom_validations = ['server_rack_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.delete_server_rack
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    @property
    def delete_server_rack(self):
        Unit.objects.filter(server_rack=self.server_rack).delete()
        self.server_rack.delete()
        return None

    @property
    @lru_cache()
    def server_rack(self):
        try:
            return ServerRack.objects.get(id=self.cleaned_data['id'])
        except ServerRack.DoesNotExist:
            return None

    def server_rack_presence(self):
        if not self.server_rack:
            self.add_error('id', ObjectDoesNotExist(f'Server rack id={self.cleaned_data["id"]} '
                                                    'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

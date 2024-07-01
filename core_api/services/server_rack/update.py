from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from utils.services import ServiceWithResult
from models_app.models.server_rack import ServerRack


class UpdateServerRackService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    title = forms.CharField(required=False)
    max_power = forms.IntegerField(required=False)

    custom_validations = ['server_rack_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.update_server_rack
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def update_server_rack(self):
        server_rack = self.server_rack
        if self.cleaned_data['title']:
            server_rack.title = self.cleaned_data['title']
        if self.cleaned_data['max_power']:
            server_rack.max_power = self.cleaned_data['max_power']
        server_rack.save()
        return server_rack

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

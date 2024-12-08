from django import forms
from functools import lru_cache
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from rest_framework import status

from models_app.models import User, Access
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import ServerRack


class ServerRackService(ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['server_rack_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self.server_rack
            self.response_status = status.HTTP_200_OK
        return self

    @property
    @lru_cache()
    def server_rack(self):
        try:
            return ServerRack.objects.get(id=self.cleaned_data['id'])
        except ServerRack.DoesNotExist:
            return None

    @property
    def access(self):
        try:
            return Access.objects.get(user=self.cleaned_data['current_user'],
                                      scheme=self.server_rack.room.building.scheme)
        except Access.DoesNotExist:
            return None

    def server_rack_presence(self):
        if not self.server_rack:
            self.add_error('id', ObjectDoesNotExist(f'Server rack id={self.cleaned_data["id"]} '
                                                    'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self):
        if self.server_rack:
            if not self.access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self.server_rack.room.building.scheme.id} '
                                                                'is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

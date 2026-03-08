from django import forms
from functools import lru_cache

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status

from core_api.utils.access_checker import scope_for_server_rack
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, ServerRack
from utils.fields import ModelField
from utils.services import ServiceWithResult


class DeleteServerRackService(ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['server_rack_presence', 'access_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._delete_server_rack()
            self.response_status = status.HTTP_204_NO_CONTENT
        return self

    def _delete_server_rack(self) -> None:
        self._server_rack.delete()

    def get_access_scope(self):
        return scope_for_server_rack(self._server_rack)

    @property
    @lru_cache()
    def _server_rack(self) -> ServerRack | None:
        try:
            return ServerRack.objects.select_related('room', 'room__building').get(id=self.cleaned_data['id'])
        except ServerRack.DoesNotExist:
            return None

    def server_rack_presence(self) -> None:
        if not self._server_rack:
            self.add_error('id', ObjectDoesNotExist(f'Server rack id={self.cleaned_data["id"]} '
                                                    'not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

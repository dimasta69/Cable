from django import forms
from functools import lru_cache

from rest_framework import status

from core_api.utils.access_checker import AccessChecker, scope_for_server_rack
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from models_app.models import User, ServerRack
from utils.fields import ModelField
from utils.services import ServiceWithResult


class ServerRackService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    access_required_roles = AccessChecker.ROLES_READ
    custom_validations = ['run_presence_checks', 'access_presence']
    presence_checks = [("_server_rack", "id", "Server rack")]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._server_rack
            self.response_status = status.HTTP_200_OK
        return self

    def get_access_scope(self):
        return scope_for_server_rack(self._server_rack)

    @property
    @lru_cache()
    def _server_rack(self) -> ServerRack | None:
        try:
            return ServerRack.objects.select_related('room', 'room__building').get(id=self.cleaned_data['id'])
        except ServerRack.DoesNotExist:
            return None

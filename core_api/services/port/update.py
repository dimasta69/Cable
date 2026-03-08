from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from rest_framework import status
from functools import lru_cache
from typing import List

from core_api.utils.access_checker import scope_for_equipment
from core_api.utils.presence import PresenceChecksMixin
from core_api.utils.scheme_access import ResourceAccessMixin
from utils.fields import ModelField, ListIntegerField
from utils.services import ServiceWithResult
from core_api.utils.change_mode_port import change_mode_port
from models_app.models import Port, User, LineType, PortMode


class UpdatePortService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    line_type_id = ListIntegerField(required=False)
    mode_id = forms.IntegerField(required=False)
    mac = forms.CharField(
        max_length=17,
        validators=[
            RegexValidator(
                regex=r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
                message='Введите корректный MAC-адрес.',
                code='invalid_mac_address'
            )
        ],
        required=False
    )
    current_user = ModelField(User)

    custom_validations = ['run_presence_checks', 'line_type_presence', 'access_presence']
    presence_checks = [
        ("_port", "id", "Port"),
        ("_mode", "mode_id", "Port mode", True),
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._update_port
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _update_port(self) -> Port:
        port = self._port
        if self.cleaned_data.get('line_type_id'):
            port.line_type = self._line_type
        if self.cleaned_data.get('mode_id'):
            change_mode_port(port.pk)
            port.mode = self._mode
        if self.cleaned_data.get('mac'):
            port.mac = self.cleaned_data['mac']
        port.save()
        return port

    def get_access_scope(self):
        if self._port and getattr(self._port, 'equipment', None):
            return scope_for_equipment(self._port.equipment)
        return None

    @property
    @lru_cache()
    def _port(self) -> Port | None:
        try:
            return Port.objects.select_related(
                'equipment',
                'equipment__scheme',
                'equipment__room',
                'equipment__room__building',
            ).prefetch_related(
                'equipment__units__server_rack__room__building',
            ).get(id=self.cleaned_data['id'])
        except Port.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _line_type(self) -> List[LineType]:
        try:
            return LineType.objects.filter(id__in=self.cleaned_data.get('line_type_id') or [])
        except LineType.DoesNotExist:
            return LineType.objects.none()

    @property
    @lru_cache()
    def _mode(self) -> PortMode | None:
        try:
            return PortMode.objects.get(id=self.cleaned_data['mode_id'])
        except PortMode.DoesNotExist:
            return None

    def line_type_presence(self) -> None:
        if self.cleaned_data.get('line_type_id'):
            if len(self._line_type) != len(self.cleaned_data['line_type_id']):
                self.add_error(
                    'line_type_id',
                    ObjectDoesNotExist("Line type ids not found")
                )
                self.response_status = status.HTTP_404_NOT_FOUND


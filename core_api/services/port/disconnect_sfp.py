from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from functools import lru_cache
from typing import List

from core_api.utils.access_checker import AccessChecker, scope_for_equipment
from utils.services import ServiceWithResult
from utils.fields import ListIntegerField, ModelField
from models_app.models import Port, User


class DisconnectSfpService(ServiceWithResult):
    port_list = ListIntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = ['port_presence', 'access_port_presence']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self._disconnect_sfp()
            self.response_status = status.HTTP_200_OK
        return self

    def _disconnect_sfp(self) -> None:
        for port in self._ports:
            port.sfp = None
        Port.objects.bulk_update(self._ports, ['sfp'])

    @property
    @lru_cache()
    def _ports(self) -> List[Port]:
        try:
            return list(
                Port.objects.filter(
                    id__in=self.cleaned_data['port_list'],
                    front_side__isnull=True,
                ).select_related(
                    'equipment',
                    'equipment__scheme',
                    'equipment__room',
                    'equipment__room__building',
                ).prefetch_related(
                    'equipment__units__server_rack__room__building',
                )
            )
        except Port.DoesNotExist:
            return []

    def port_presence(self) -> None:
        if len(self.cleaned_data['port_list']) != len(self._ports):
            if not self._ports:
                self.add_error('port_list', ObjectDoesNotExist('Port list does not exist'))
                self.response_status = status.HTTP_404_NOT_FOUND

    def access_port_presence(self) -> None:
        if not self._ports:
            return
        user = self.cleaned_data['current_user']
        for port in self._ports:
            scope = scope_for_equipment(port.equipment)
            if not AccessChecker.has_permission(user, AccessChecker.ROLES_CHANGE, scope):
                self.add_error(
                    'port_list',
                    PermissionError(f"Access with port id={port.id} not found"),
                )
                self.response_status = status.HTTP_403_FORBIDDEN
                return

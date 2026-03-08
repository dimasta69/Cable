from django import forms
from functools import lru_cache
from typing import List

from django.core.exceptions import ValidationError
from rest_framework import status

from core_api.utils.access_checker import AccessChecker, scope_for_equipment
from core_api.utils.presence import PresenceChecksMixin
from utils.fields import ModelField, ListIntegerField
from utils.services import ServiceWithResult
from models_app.models import Port, SfpTemplate, User


class AddToPortSfpService(PresenceChecksMixin, ServiceWithResult):
    id = forms.IntegerField(required=True)
    port_list = ListIntegerField(required=True)
    current_user = ModelField(User)

    custom_validations = [
        'run_presence_checks', 'speed_control', 'check_ports', 'access_port_presence', 'line_type_control',
    ]
    presence_checks = [("_sfp_template", "id", "Sfp template", True)]  # only_if_set

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._add_sfp
            self.response_status = status.HTTP_200_OK
        return self

    @property
    def _add_sfp(self) -> List[Port]:
        for port in self._port_list:
            port.sfp = self._sfp_template
        Port.objects.bulk_update(self._port_list, ['sfp'])
        return self._port_list

    @property
    @lru_cache()
    def _port_list(self):
        try:
            return Port.objects.filter(
                id__in=self.cleaned_data["port_list"],
                sfp__isnull=True,
                front_side__isnull=True,
                port_template__modular=True,
            ).select_related(
                "equipment",
                "equipment__scheme",
                "equipment__template__manufacturer",
                "equipment__template__type",
                "equipment__room",
                "equipment__room__building",
            ).prefetch_related(
                "equipment__units",
                "equipment__units__server_rack",
                "equipment__units__server_rack__room",
                "equipment__units__server_rack__room__building",
            )
        except Port.DoesNotExist:
            return Port.objects.none()

    @property
    @lru_cache()
    def _sfp_template(self) -> SfpTemplate | None:
        try:
            return SfpTemplate.objects.prefetch_related("speed").get(id=self.cleaned_data['id'])
        except SfpTemplate.DoesNotExist:
            return None

    def check_ports(self) -> None:
        if len(self._port_list) != len(self.cleaned_data['port_list']):
            self.add_error(
                "port_list",
                ValidationError(
                    "Проверьте передаваемы порты на наличие подключений, находятся ли в них sfp модуль,"
                    " правильно ли вы передаете все id портов, его модульность"
                )
            )

    def speed_control(self) -> None:
        if self._port_list and self._sfp_template:
            sfp_speeds = self._sfp_template.speed.all()
            for port in self._port_list:
                speed_set = set(port.port_template.speed.all())
                if not speed_set & set(sfp_speeds):
                    self.add_error(
                        "id",
                        ValidationError(
                            f"Sfp with={self._sfp_template.id} не совпадают скорости с портом port_id={port.id}"
                        )
                    )

    def line_type_control(self) -> None:
        line_types = {
            item["port_template__line_type"]
            for item in self._port_list.values("port_template__line_type")
        }
        if not set(line_types) & set(self._sfp_template.line_type.values_list("id", flat=True)):
            self.add_error(
                "id",
                ValidationError("The given ports do not correspond to sfp in line_type"),
            )
            self.response_status = status.HTTP_400_BAD_REQUEST

    def access_port_presence(self) -> None:
        if not self._port_list:
            return
        user = self.cleaned_data['current_user']
        for port in self._port_list:
            scope = scope_for_equipment(port.equipment)
            if not AccessChecker.has_permission(user, AccessChecker.ROLES_CHANGE, scope):
                self.add_error(
                    "port_list",
                    PermissionError(f"Access with port id={port.id} not found"),
                )
                self.response_status = status.HTTP_403_FORBIDDEN
                return

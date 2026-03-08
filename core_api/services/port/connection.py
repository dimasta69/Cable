from django import forms
from django.core.exceptions import ValidationError
from django.contrib.postgres.forms import SimpleArrayField
from django.db import transaction
from rest_framework import status
from functools import lru_cache

from core_api.utils.access_checker import AccessChecker, scope_for_equipment
from core_api.utils.connection import connection
from utils.fields import ModelField
from utils.services import ServiceWithResult
from models_app.models import Port, User


class ConnectionPortService(ServiceWithResult):
    front_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)
    back_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)
    current_user = ModelField(User)

    custom_validations = [
        'ports_presence', 'free_ports', 'backside_and_active_equipment', 'access_port_presence', 'ports_modular',
    ]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            with transaction.atomic():
                side = self._front_or_back_side()
                port_1, port_2, side = self._lines_is_null(side)
                connection(port_1, port_2, side)
        return self

    def _front_or_back_side(self) -> tuple[str, str]:
        if self.cleaned_data.get('front_port_list'):
            return "front_side", "front_port_list"
        elif self.cleaned_data.get('back_port_list'):
            return "back_side", "back_port_list"

    def _lines_is_null(self, side: tuple[str, str]) -> tuple[Port, Port, str]:
        port_1 = self._ports.get(id=self.cleaned_data[side[1]][0])
        port_2 = self._ports.get(id=self.cleaned_data[side[1]][1])
        setattr(port_1, side[0], port_2)
        setattr(port_2, side[0], port_1)
        port_1.save()
        port_2.save()
        return port_1, port_2, side[0]

    @property
    @lru_cache()
    def _ports(self):
        try:
            ports = []
            if self.cleaned_data.get('front_port_list'):
                ports = self.cleaned_data['front_port_list']
            if self.cleaned_data.get('back_port_list'):
                ports = self.cleaned_data['back_port_list']
            return Port.objects.filter(id__in=ports).select_related(
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
            return None

    def ports_presence(self) -> None:
        if self._ports is None or len(self._ports) != 2:
            self.add_error('ports', ValidationError("Ports does not exist"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def free_ports(self) -> None:
        if self._ports and len(self._ports) == 2:
            for i in self._ports:
                if self.cleaned_data['front_port_list'] and i.front_side is not None:
                    self.add_error('front_port_list', ValidationError(f'Port id={i.id} already connected'))
                elif self.cleaned_data['back_port_list'] and i.back_side is not None:
                    self.add_error('back_port_list', ValidationError(f'Port id={i.id} already connected'))

    def backside_and_active_equipment(self) -> None:
        if self.cleaned_data['back_port_list'] and self._ports:
            for port in self._ports:
                if port.equipment.template.type.is_active:
                    self.add_error('back_port_list', ValidationError('It is not possible to'
                                                                     ' connect to active equipment at "back_side"')
                                   )

    def ports_modular(self) -> None:
        if self._ports and len(self._ports) == 2:
            if self._ports[0].port_template.modular and self._ports[0].sfp is None:
                self.add_error(
                    "front_port_list",
                    ValidationError(f"SFP не поделючено в порт={self._ports[0].id}")
                )
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            if self._ports[1].port_template.modular and self._ports[1].sfp is None:
                self.add_error(
                    "front_port_list",
                    ValidationError(f"SFP не поделючено в порт={self._ports[1].id}")
                )
                self.response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    def speed_match(self) -> None:
        if self._ports and len(self._ports) == 2:
            if self._ports[0].equipment.template.type.is_active and self._ports[1].equipment.template.type.is_active:
                try:
                    if not self._ports[0].port_template.modular:
                        speed_1 = self._ports[0].port_template.speed.values("value")
                    else:
                        if hasattr(self._ports, 'sfp'):
                            speed_1 = self._ports.sfp.speed.values("value")
                        else:
                            raise AttributeError(f"В порту id={self._ports[0].id} отсутсвует sfp")
                except AttributeError as e:
                    self.add_error("front_port_list", e)
                    return None

                try:
                    if not self._ports[1].port_template.modular:
                        speed_2 = self._ports[1].port_template.speed.values("value")
                    else:
                        if hasattr(self._ports, 'sfp'):
                            speed_2 = self._ports.sfp.speed.values("value")
                        else:
                            raise AttributeError(f"В порту id={self._ports[1].id} отсутсвует sfp")
                except AttributeError as e:
                    self.add_error("front_port_list", e)
                    return None

                if not set(speed_1) & set(speed_2):
                    self.add_error("front_port_list", ValidationError("У портов не совпадают скорости"))

    def access_port_presence(self) -> None:
        if not self._ports or len(self._ports) != 2:
            return
        user = self.cleaned_data['current_user']
        for i, port in enumerate(self._ports):
            equipment = port.equipment
            scope = scope_for_equipment(equipment)
            if not AccessChecker.has_permission(user, AccessChecker.ROLES_CHANGE, scope):
                field = "front_port_list" if self.cleaned_data.get("front_port_list") else "back_port_list"
                self.add_error(
                    field,
                    PermissionError(f"Access with port id={port.id} not found"),
                )
                self.response_status = status.HTTP_403_FORBIDDEN

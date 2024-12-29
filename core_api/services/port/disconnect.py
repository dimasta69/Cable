from functools import lru_cache

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.db import transaction
from rest_framework import status

from models_app.models import Port
from utils.errors import ValidationError
from utils.services import ServiceWithResult
from core_api.utils.connection import delete_past_line, disconnect, new_lines


class DisconnectPortService(ServiceWithResult):
    front_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)
    back_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)

    custom_validations = ["ports_presence", "free_ports"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            with transaction.atomic():
                side = self._front_or_back_side()
                port_1, port_2, side = self._lines_is_null(side)
                line_1, line_2 = disconnect(port_1, port_2)
                delete_past_line(port_1, port_2)
                new_lines(port_1, port_2, line_1, line_2)
        return self

    def _front_or_back_side(self) -> tuple[str, str]:
        if self.cleaned_data.get('front_port_list'):
            return "front_side", "front_port_list"
        elif self.cleaned_data.get('back_port_list'):
            return "back_side", "back_port_list"

    def _lines_is_null(self, side: tuple[str, str]) -> tuple[Port, Port, str]:
        port_1 = self._ports.get(id=self.cleaned_data[side[1]][0])
        port_2 = self._ports.get(id=self.cleaned_data[side[1]][1])
        setattr(port_1, side[0], None)
        setattr(port_2, side[0], None)
        port_1.save()
        port_2.save()
        return port_1, port_2, side[0]

    @property
    @lru_cache()
    def _ports(self) -> Port | None:
        try:
            ports = []
            if self.cleaned_data['front_port_list']:
                ports = self.cleaned_data['front_port_list']
            if self.cleaned_data['back_port_list']:
                ports = self.cleaned_data['back_port_list']
            return Port.objects.filter(id__in=ports).select_related(
                "equipment",
                "equipment__template__manufacturer",
                "equipment__template__type",
                "equipment__room",
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
            self.add_error('ports', ValidationError(f"Ports does not exist"))
            self.response_status = status.HTTP_404_NOT_FOUND

    def free_ports(self) -> None:
        if self._ports and len(self._ports) == 2:
            for i in self._ports:
                if self.cleaned_data['front_port_list'] and i.front_side is None:
                    self.add_error('front_port_list', ValidationError(f'Port id={i.id} already connected'))
                elif self.cleaned_data['back_port_list'] and i.back_side is None:
                    self.add_error('back_port_list', ValidationError(f'Port id={i.id} already connected'))

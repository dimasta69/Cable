import json

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.postgres.forms import SimpleArrayField
from django.db import transaction
from rest_framework import status
from functools import lru_cache
from typing import Literal, Tuple

from utils.services import ServiceWithResult
from models_app.models import Port, Line


def port_json(port: Port, side: Literal["front_side", "back_side"]) -> json:
    return {
        "port_id": str(port.pk),
        "side": side,
        "uid": str(port.uid),
        "equipment_id": str(port.equipment.id),
        "equipment_manufacturer": str(port.equipment.template.manufacturer),
        "equipment_type": str(port.equipment.template.type),
        "equipment_model": str(port.equipment.template.model),

        "server_rack_id": str(port.equipment.units.first().server_rack.id)
        if not port.equipment.room else None,

        "unit_uuid": str(port.equipment.units.first().uid)
        if not port.equipment.room else None,

        "unit_side": str(port.equipment.units.first().side)
        if not port.equipment.room else None,

        "room_id": str(port.equipment.units.first().server_rack.room.id)
        if not port.equipment.room else str(port.equipment.room.id),

        "room_floor": str(port.equipment.units.first().server_rack.room.floor)
        if not port.equipment.room else str(port.equipment.room.floor),

        "room_number": str(port.equipment.units.first().server_rack.room.number)
        if not port.equipment.room else str(port.equipment.room.number),

        "is_server_room": str(port.equipment.units.first().server_rack.room.is_server_room)
        if not port.equipment.room else str(port.equipment.room.is_server_room),

        "building_id": str(port.equipment.units.first().server_rack.room.building.id)
        if not port.equipment.room else str(port.equipment.room.bulding.id),

        "building_name": str(port.equipment.units.first().server_rack.room.building.name)
        if not port.equipment.room else str(port.equipment.room.bulding.name),
    }


class ConnectionPortService(ServiceWithResult):
    front_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)
    back_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)

    custom_validations = ['ports_presence', 'free_ports', 'backside_and_active_equipment']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            with transaction.atomic():
                side = self._front_or_back_side()
                port_1, port_2, side = self._lines_is_null(side)
                line = self._create_line(port_1, port_2, side)
                self._delete_past_line(port_1, port_2)
                self._connection_port(line)
        return self

    def _front_or_back_side(self) -> tuple[str, str]:
        if self.cleaned_data.get('front_port_list'):
            return "front_side", "front_port_list"
        elif self.cleaned_data.get('back_port_list'):
            return "back_side", "back_port_list"

    def _lines_is_null(self, side: tuple[str, str]) -> Tuple[Port, Port, str]:
        port_1 = self._ports.get(id=self.cleaned_data[side[1]][0])
        port_2 = self._ports.get(id=self.cleaned_data[side[1]][1])
        setattr(port_1, side[0], port_2)
        setattr(port_2, side[0], port_1)
        return port_1, port_2, side[0]

    def _create_line(self, port_1: Port, port_2: Port, side: Literal["front_side", "back_side"]) -> Line:
        if port_1.line:
            line_1 = port_1.line.connection if port_1.line.connection[-1] == port_1.pk \
                else list(reversed(port_1.line.connection))
        else:
            line_1 = [port_json(port_1, side)]

        if port_2.line:
            line_2 = port_2.line.connection if port_2.line.connection[0] == port_2.pk \
                else list(reversed(port_2.line.connection))
        else:
            line_2 = [port_json(port_2, side)]

        return Line.objects.create(connection=line_1.extend(line_2))

    def _delete_past_line(self, port_1: Port, port_2: Port) -> None:
        if port_1.line:
            port_1.line.delete()
        if port_2.line:
            port_2.line.delete()

    def _connection_port(self, line: Line) -> None:
        line_ports_id = [port['id'] for port in line.connection]
        ports_update = []
        for ids in line_ports_id:
            ports_update.append([Port(id=ids, line=line)])
        Port.objects.bulk_update(ports_update, ['line'])

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

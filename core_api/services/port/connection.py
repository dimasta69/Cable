from django import forms
from django.core.exceptions import ValidationError
from django.contrib.postgres.forms import SimpleArrayField
from django.db import transaction
from rest_framework import status
from functools import lru_cache

from utils.services import ServiceWithResult
from models_app.models import Port, Line


def port_json(port):
    return {
        str(port.id): {
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

                        "room_number": str(port.equipment.units.first().server_rack.room.number)
                        if not port.equipment.room else str(port.equipment.room.number),

                        "is_server_room": str(port.equipment.units.first().server_rack.room.is_server_room)
                        if not port.equipment.room else str(port.equipment.room.is_server_room),

                        "building_id": str(port.equipment.units.first().server_rack.room.building.id)
                        if not port.equipment.room else str(port.equipment.room.bulding.id),

                        "building_name": str(port.equipment.units.first().server_rack.room.building.name)
                        if not port.equipment.room else str(port.equipment.room.bulding.name),
                    }
    }


class ConnectionPortService(ServiceWithResult):
    front_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)
    back_port_list = SimpleArrayField(forms.IntegerField(), min_length=2, max_length=2, required=False)

    custom_validations = ['ports_presence', 'free_ports', 'backside_and_active_equipment']

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            if self.cleaned_data.get('front_port_list'):
                self._connection(True)
            elif self.cleaned_data.get('back_port_list'):
                self._connection(False)
        return self

    def _connection(self, front=True) -> None:
        with transaction.atomic():
            if front:
                port_1 = self._ports.get(id=self.cleaned_data["front_port_list"][0])
                port_2 = self._ports.get(id=self.cleaned_data["front_port_list"][1])
                port_1.front_side = port_2
                port_2.front_side = port_1
            else:
                port_1 = self._ports.get(id=self.cleaned_data["back_port_list"][0])
                port_2 = self._ports.get(id=self.cleaned_data["back_port_list"][1])
                port_1.back_side = port_2
                port_2.back_side = port_1

            line_1 = None
            line_2 = None

            if port_1.line is None and port_2.line is None:
                line_list = [port_json(port_1), port_json(port_2)]
                line = Line.objects.create(connection=line_list)
                port_1.line = line
                port_2.line = line
            else:
                if port_1.line:
                    line_1 = port_1.line.connection if port_1.line.connection[-1].keys() == port_1.id \
                        else list(reversed(port_1.line.connection))
                else:
                    port_1.line = Line.objects.create()

                if port_2.line:
                    line_2 = port_2.line.connection if port_2.line.connection[0].keys() == port_2.id \
                        else list(reversed(port_2.line.connection))

                line_1 = line_1 if line_1 else [port_json(port_1)]
                line_2 = line_2 if line_2 else [port_json(port_2)]

                line_1.extend(line_2)

                port_1.line.connection = line_1
                port_2.line.delete()
                port_2.line = port_1.line

                port_1.line.save()

            port_1.save()
            port_2.save()

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

    def free_ports(self):
        if self._ports and len(self._ports) == 2:
            for i in self._ports:
                if self.cleaned_data['front_port_list'] and i.front_side is not None:
                    self.add_error('front_port_list', ValidationError(f'Port id={i.id} already connected'))
                elif self.cleaned_data['back_port_list'] and i.back_side is not None:
                    self.add_error('back_port_list', ValidationError(f'Port id={i.id} already connected'))

    def backside_and_active_equipment(self):
        if self.cleaned_data['back_port_list'] and self._ports:
            for port in self._ports:
                if port.equipment.template.type.is_active:
                    self.add_error('back_port_list', ValidationError('It is not possible to'
                                                                     ' connect to active equipment at "back_side"')
                                   )

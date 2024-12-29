import json

from models_app.models import Port, Line
from typing import Literal


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


def create_line(port_1: Port, port_2: Port, side: Literal["front_side", "back_side"]) -> Line:
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

    line_1.extend(line_2)
    return Line.objects.create(connection=line_1)


def delete_past_line(port_1: Port, port_2: Port) -> None:
    if port_1.line:
        port_1.line.delete()
    if port_2.line:
        port_2.line.delete()


def connection_port(line: Line) -> None:
    line_ports = [port for port in line.connection]
    ports_update = []
    for port in line_ports:
        ports_update.append(Port(id=port["port_id"], line=line, equipment_id=port["equipment_id"]))
    Port.objects.bulk_update(ports_update, ['line'])

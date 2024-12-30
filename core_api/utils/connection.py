import json

from models_app.models import Line
from typing import Literal
from core_api.utils.exception import DisconnectionValueNotFound


def connection(port_1, port_2, side: Literal["front_side", "back_side"]):
    line = create_line(port_1, port_2, side)
    delete_past_line(port_1, port_2)
    connection_port(line)


def disconnection(port_1, port_2):
    line_1, line_2 = disconnect(port_1, port_2)
    delete_past_line(port_1, port_2)
    new_lines(line_1, line_2)


def delete_port_from_connection(port):
    line_1, line_2 = disconnect_delete_port(port)
    port.line.delete()
    new_lines(line_1, line_2)


def port_json(port, side: Literal["front_side", "back_side"]) -> json:
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


def create_line(port_1, port_2, side: Literal["front_side", "back_side"]) -> Line:
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


def delete_past_line(port_1, port_2) -> None:
    if port_1.line:
        port_1.line.delete()
    try:
        port_2.line.delete()
    except Exception:
        pass


def connection_port(line: Line) -> None:
    line_ports = [port for port in line.connection]
    ports_update = []
    for port in line_ports:
        ports_update.append(Port(id=port["port_id"], line=line, equipment_id=port["equipment_id"]))
    Port.objects.bulk_update(ports_update, ['line'])


def disconnect(port_1, port_2) -> tuple[Line, Line]:
    line = port_1.line.connection
    for i in range(len(line)):
        if line[i]["port_id"] == str(port_1.id):
            if line[i + 1]["port_id"] == str(port_2.id):
                line_1 = Line.objects.create(connection=line[:i])
                line_2 = Line.objects.create(connection=line[i:])
                return line_1, line_2
            elif line[i - 1]["port_id"] == str(port_2.id):
                line_2 = Line.objects.create(connection=line[:i])
                line_1 = Line.objects.create(connection=line[i:])
                return line_1, line_2
            else:
                DisconnectionValueNotFound("Порты, требуемые для отключения, не найдены")


def disconnect_delete_port(port) -> tuple[Line, Line]:
    line = port.line.connection
    for i in range(len(line)):
        if line[i]["port_id"] == str(port.id):
            line_1 = Line.objects.create(connection=line[:i - 1])
            line_2 = Line.objects.create(connection=line[i + 1:])
            return line_1, line_2
        else:
            DisconnectionValueNotFound("Порты, требуемые для отключения, не найдены")


def new_lines(line_1: Line, line_2: Line) -> None:
    from models_app.models import Port
    ports_1 = Port.objects.filter(id__in=[port['port_1'] for port in line_1.connection])
    ports_2 = Port.objects.filter(id__in=[port['port_1'] for port in line_2.connection])

    ports_1.update(line=line_1)
    ports_2.update(line=line_2)

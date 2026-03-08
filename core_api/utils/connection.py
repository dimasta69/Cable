"""
Логика соединения портов (линии).

Линия — односвязный список портов: head → front_side → … → tail.
Порядок хранится в связях Port.front_side / Port.back_side; Line.connection
собирается обходом от головы (см. PROJECT.md).
"""
from typing import Literal

from models_app.models import Line, Port
from core_api.utils.exception import DisconnectionValueNotFound


# --- Обход цепочки портов (односвязный список) ---


def get_chain_head(port: Port) -> Port:
    """Возвращает «голову» цепочки: идём по back_side до начала."""
    current = port
    while current.back_side_id is not None:
        current = current.back_side
    return current


def get_chain_tail(port: Port) -> Port:
    """Возвращает «хвост» цепочки: идём по front_side до конца."""
    current = port
    while current.front_side_id is not None:
        current = current.front_side
    return current


def ports_from_head(head: Port):
    """
    Обход от головы до хвоста по front_side (односвязный список).
    Возвращает итератор портов в порядке линии.
    """
    current = head
    while current:
        yield current
        if current.front_side_id is None:
            break
        current = current.front_side


def connection_list_from_chain(port: Port, side: Literal["front_side", "back_side"]) -> list:
    """
    Строит список connection (dict для Line.connection) обходом цепочки от головы.
    port — любой порт в цепочке (после соединения port_1 и port_2).
    """
    head = get_chain_head(port)
    return [port_json(p, side) for p in ports_from_head(head)]


# --- Публичный API ---


def connection(port_1: Port, port_2: Port, side: Literal["front_side", "back_side"]) -> None:
    """Соединяет две линии (или два порта) в одну; цепочка строится обходом по front_side."""
    line = create_line(port_1, port_2, side)
    delete_past_line(port_1, port_2)
    connection_port(line)


def disconnection(port_1: Port, port_2: Port) -> None:
    line_1, line_2, ids_to_clear = disconnect(port_1, port_2)
    delete_past_line(port_1, port_2)
    new_lines(line_1, line_2)
    if ids_to_clear:
        Port.objects.filter(id__in=[int(pid) for pid in ids_to_clear]).update(line=None)


def delete_port_from_connection(port: Port) -> None:
    line_1, line_2, ids_to_clear = disconnect_delete_port(port)
    new_lines(line_1, line_2)
    if ids_to_clear:
        Port.objects.filter(id__in=[int(pid) for pid in ids_to_clear]).update(line=None)
    if port.line_id:
        port.line.delete()


def port_json(port: Port, side: Literal["front_side", "back_side"]) -> dict:
    return {
        "port_id": str(port.pk),
        "side": side,
        "uid": str(port.uid),
        "equipment_id": str(port.equipment.id),
        "equipment_manufacturer": str(port.equipment.template.manufacturer),
        "equipment_type": str(port.equipment.template.type),
        "equipment_is_active": str(port.equipment.template.type.is_active),
        "equipment_model": str(port.equipment.template.model),
        "server_rack_id": str(port.equipment.units.first().server_rack.id)
        if not port.equipment.room else None,
        "server_rack_title": str(port.equipment.units.first().server_rack.title)
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
        if not port.equipment.room else str(port.equipment.room.building.id),
        "building_name": str(port.equipment.units.first().server_rack.room.building.name)
        if not port.equipment.room else str(port.equipment.room.building.name),
    }


def create_line(port_1: Port, port_2: Port, side: Literal["front_side", "back_side"]) -> Line:
    """
    Создаёт одну линию из двух портов (или двух линий).
    Порядок берётся из цепочки: после вызова сервиса port_1.front_side = port_2,
    обходим от головы по front_side и собираем connection.
    """
    connection_list = connection_list_from_chain(port_1, side)
    return Line.objects.create(connection=connection_list)


def delete_past_line(port_1: Port, port_2: Port) -> None:
    if port_1.line_id:
        port_1.line.delete()
    if port_2.line_id and port_2.line_id != getattr(port_1, "line_id", None):
        try:
            port_2.line.delete()
        except Exception:
            pass


def connection_port(line: Line) -> None:
    """Привязывает все порты линии к line (обход по connection)."""
    ports_update = [
        Port(id=int(p["port_id"]), line=line, equipment_id=int(p["equipment_id"]))
        for p in line.connection
    ]
    if ports_update:
        Port.objects.bulk_update(ports_update, ["line"])


def disconnect(port_1: Port, port_2: Port) -> tuple[Line | None, Line | None, list[str]]:
    """
    Разбивает линию на две по паре соседних портов.
    Ожидается, что связь front_side/back_side между port_1 и port_2 уже сброшена сервисом.
    Третий элемент — id портов, у которых нужно сбросить line (сегмент из одного порта).
    """
    line_data = port_1.line.connection
    n = len(line_data)
    for i in range(n):
        if int(line_data[i]["port_id"]) != port_1.id:
            continue
        line_1 = None
        line_2 = None
        ids_to_clear = []
        if i + 1 < n and int(line_data[i + 1]["port_id"]) == port_2.id:
            if len(line_data[: i + 1]) > 1:
                line_1 = Line.objects.create(connection=line_data[: i + 1])
            else:
                ids_to_clear.extend(p["port_id"] for p in line_data[: i + 1])
            if len(line_data[i + 1 :]) > 1:
                line_2 = Line.objects.create(connection=line_data[i + 1 :])
            else:
                ids_to_clear.extend(p["port_id"] for p in line_data[i + 1 :])
            return line_1, line_2, ids_to_clear
        if i - 1 >= 0 and int(line_data[i - 1]["port_id"]) == port_2.id:
            if len(line_data[:i]) > 1:
                line_2 = Line.objects.create(connection=line_data[:i])
            else:
                ids_to_clear.extend(p["port_id"] for p in line_data[:i])
            if len(line_data[i:]) > 1:
                line_1 = Line.objects.create(connection=line_data[i:])
            else:
                ids_to_clear.extend(p["port_id"] for p in line_data[i:])
            return line_1, line_2, ids_to_clear
        raise DisconnectionValueNotFound(
            "Порты, требуемые для отключения, не найдены"
        )
    raise DisconnectionValueNotFound(
        "Порты, требуемые для отключения, не найдены"
    )


def disconnect_delete_port(port: Port) -> tuple[Line | None, Line | None, list[str]]:
    """
    Удаляет порт из линии; линия разбивается на две (или одну, если порт был с краю).
    Третий элемент — id портов, у которых нужно сбросить line (сегмент из одного порта).
    """
    if not port.line_id:
        return None, None, []
    line_data = port.line.connection
    for i in range(len(line_data)):
        if int(line_data[i]["port_id"]) != port.id:
            continue
        line_1 = None
        line_2 = None
        ids_to_clear = []
        if len(line_data[:i]) > 1:
            line_1 = Line.objects.create(connection=line_data[:i])
        else:
            ids_to_clear.extend(p["port_id"] for p in line_data[:i])
        if len(line_data[i + 1 :]) > 1:
            line_2 = Line.objects.create(connection=line_data[i + 1 :])
        else:
            ids_to_clear.extend(p["port_id"] for p in line_data[i + 1 :])
        return line_1, line_2, ids_to_clear
    raise DisconnectionValueNotFound(
        "Порты, требуемые для отключения, не найдены"
    )


def new_lines(line_1: Line | None, line_2: Line | None) -> None:
    """Привязывает порты к новым линиям после разрыва."""
    if line_1:
        ids_1 = [p["port_id"] for p in line_1.connection]
        Port.objects.filter(id__in=ids_1).update(line=line_1)
    if line_2:
        ids_2 = [p["port_id"] for p in line_2.connection]
        Port.objects.filter(id__in=ids_2).update(line=line_2)

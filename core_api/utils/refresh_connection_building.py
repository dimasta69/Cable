from models_app.models import Equipment, ServerRack, Building
from typing import List


def refresh_connection_building(building: Building) -> None:
    building_connection = []
    building_connection.append(
        [list[map(refresh_connection_server_rack, server_rack)] for server_rack in building.server_racks]
    )
    building.connection = [set(building_connection)]
    building.save()


def refresh_connection_server_rack(server_rack: ServerRack) -> list[int]:
    equipment_connection = equipment_connection_passive(server_rack)
    server_rack_connection = port_connection_back_side(equipment_connection)
    return [set(server_rack_connection)]


def equipment_connection_passive(server_rack: ServerRack) -> List[Equipment]:
    equipments_passive_list = [
        unit.equipment
        for unit in server_rack.units.all()
        if unit.equipment and unit.equipment.template.type.is_active is False
    ]
    return equipments_passive_list


def port_connection_back_side(equipment_passive_list: List[Equipment]) -> list[int]:
    server_rack_connection = []
    for equipment in equipment_passive_list:
        server_rack_connection.append(
            [
                port.equipment.units.all()[0].server_rack.room.building.id
                for port in equipment.ports if port.back_side is not None
            ]
        )
    return server_rack_connection

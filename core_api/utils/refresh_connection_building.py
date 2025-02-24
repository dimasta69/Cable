from models_app.models import Building, Scheme
from models_app.models.port.models import Port
from django.db import transaction
from typing import List, Dict


def refresh_connection_building(scheme: Scheme) -> None:
    building_to_update = prepared_building_to_update(scheme)
    with transaction.atomic():
        Building.objects.bulk_update(building_to_update, ['connection'])


def delete_connection_build(scheme: Scheme) -> None:
    Building.objects.filter(scheme=scheme).update(connection=None)


def prepared_building_to_update(scheme: Scheme) -> List[Building]:
    ports = port_list(scheme)
    building_connection = set_building_connection(ports)
    building_to_update = create_buildings_to_update(building_connection)
    return building_to_update


def port_list(scheme: Scheme) -> List[Port]:
    ports = Port.objects.filter(
        equipment__scheme=scheme,
        equipment__template__type__is_active=False,
        back_side__isnull=False,
        back_side__equipment__room__isnull=True,
    )
    return ports


def set_building_connection(ports: List[Port]) -> Dict[Building, List[int]]:
    building_connection = {}
    for port in ports:
        building = port.equipment.units.first().server_rack.room.building
        connection_id = port.back_side.equipment.units.first().server_rack.room.building.id

        if building in building_connection:
            building_connection[building].append(connection_id)
        else:
            building_connection[building] = [connection_id]
    return building_connection


def create_buildings_to_update(building_connection: Dict[Building, List[int]]) -> List[Building]:
    building_to_update = []
    for building, connection in building_connection.items():
        building.connection = connection
        building_to_update.append(building)

    return building_to_update

from models_app.models import Equipment, ServerRack, Building, Unit
from typing import List
from models_app.models.scheme.models import Scheme
from models_app.models.port.models import Port
from django.db import transaction


# def refresh_connection_building(building: Building) -> None:
#     building_connection = []
#     building_connection.append(
#         [
#             list(
#                 map(refresh_connection_server_rack, server_rack)
#             ) for server_rack in building.rooms.all().values_list("server_rack")
#         ]
#     )
#     building.connection = [set(building_connection)]
#     building.save()


# def refresh_connection_server_rack(server_rack_id: int) -> list[int]:
#     equipment_connection = equipment_connection_passive(server_rack_id)
#     server_rack_connection = port_connection_back_side(equipment_connection)
#     return [set(server_rack_connection)]


# def equipment_connection_passive(server_rack_id: int) -> List[Equipment]:
#     equipments_passive_list = [
#         unit.equipment
#         for unit in server_rack.units.all()
#         if unit.equipment and unit.equipment.template.type.is_active is False
#     ]

#     equipments_passive_list = Unit.objects.filter(
#         server_rack_id=server_rack_id, equipment__isnull=False, equipment__template__type__is_active=False
#     )
#     return [equipments_passive_list]


# def port_connection_back_side(equipment_passive_list: List[Equipment]) -> list[int]:
#     server_rack_connection = []
#     for equipment in equipment_passive_list:
#         server_rack_connection.append(
#             [
#                 port.equipment.units.all()[0].server_rack.room.building.id
#                 for port in equipment.ports if port.back_side is not None
#             ]
#         )
#     return server_rack_connection


# def refresh_connection_building(building: Building, scheme) -> None:
#     building_connection = []
#     building_connection.append(
#         [
#             list(
#                 map(refresh_connection_server_rack, ServerRack.objects.filter(room__building__scheme=scheme, ))
#             ) for server_rack in building.rooms.all().values_list("server_rack")
#         ]
#     )
#     building.connection = [set(building_connection)]
#     building.save()


def refresh_connection_building(scheme: Scheme) -> None:
    building_connection = {}
    ports = Port.objects.filter(
        equipment__scheme=scheme,
        equipment__template__type__is_active=False,
        back_side__isnull=False,
        back_side__equipment__room__isnull=True,
    )

    building_connection = {}

    for port in ports:
        building = port.equipment.units.first().server_rack.room.building
        connection_id = port.back_side.equipment.units.first().server_rack.room.building.id

        if building in building_connection:
            building_connection[building].append(connection_id)
        else:
            building_connection[building] = [connection_id]

    objects_to_update = []
    for building, connection in building_connection.items():
        building.connection = connection
        objects_to_update.append(building)

    with transaction.atomic():
        Building.objects.bulk_update(objects_to_update, ['connection'])

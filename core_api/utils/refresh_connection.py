import json

from models_app.models import EquipmentScheme, Port


def refresh_connection_is_active(equipment_scheme: EquipmentScheme) -> None:
    ports = Port.objects.filter(equipment=equipment_scheme.equipment, line__isnull=False).select_related(
        'line',
        'equipment',
        'equipment__template__type',
    )

    equipments_active = set()
    equipments_is_not_active = set()

    if equipment_scheme.equipment.template.type.is_active:
        for port in ports:
            port_connection = port.line.connection
            for i in range(len(port_connection)):
                if port_connection[i]['equipment_is_active'] == "True":
                    equipments_active.add(int(port_connection[i]["equipment_id"]))
                if int(port_connection[i]['equipment_id']) == equipment_scheme.equipment.id:
                    if i - 1 >= 0:
                        equipments_is_not_active.add(int(port_connection[i - 1]["equipment_id"]))
                    if len(port_connection) > i + 1:
                        equipments_is_not_active.add(int(port_connection[i + 1]["equipment_id"]))

    elif not equipment_scheme.equipment.template.type.is_active:
        equipments_active = None
        for port in ports:
            port_connection = port.line.connection
            for i in range(len(port_connection)):
                if int(port_connection[i]['equipment_id']) == equipment_scheme.equipment.id:
                    if i - 1 >= 0:
                        equipments_is_not_active.add(int(port_connection[i - 1]["equipment_id"]))
                    if len(port_connection) > i + 1:
                        equipments_is_not_active.add(int(port_connection[i + 1]["equipment_id"]))

    if equipments_active:
        equipment_scheme.connection_active = list(equipments_active)
    else:
        equipment_scheme.connection_active = None
    equipment_scheme.connection_passive = list(equipments_is_not_active)
    equipment_scheme.save()

from models_app.models import EquipmentSchemeIsActive, Port
from django.core.exceptions import ValidationError


def refresh_connection_is_active(equipment_scheme: EquipmentSchemeIsActive):
    ports = Port.objects.filter(equipment=equipment_scheme.equipment, line__isnull=False).select_related('line')

    equipments_active = set()
    equipments_is_not_active = set()

    for port in ports:
        port_connection = port.line.connection
        for i in range(len(port_connection)):
            if port_connection[i]['equipment_is_active']:
                equipments_active.add(int(port_connection[i]["equipment_id"]))
            if int(port_connection[i]['equipment_id']) == equipment_scheme.equipment.id:
                try:
                    equipments_is_not_active.add(int(port_connection[i-1]["equipment_id"]))
                except IndexError:
                    pass

                try:
                    equipments_is_not_active.add(int(port_connection[i+1]["equipment_id"]))
                except IndexError:
                    pass

    equipment_scheme.connection_active = list(equipments_active)
    equipment_scheme.connection_passive = list(equipments_is_not_active)
    equipment_scheme.save()

from models_app.models import EquipmentSchemeIsActive, Port
from django.core.exceptions import ValidationError


def refresh_connection_is_active(equipment_scheme: EquipmentSchemeIsActive):
    ports = Port.objects.filter(equipment=equipment_scheme.equipment, line__isnull=False).select_related('line')

    equipments_active = set()
    equipments_is_not_active = set()

    for port in ports:
        for port_connection in port.line.connection:
            if port_connection['equipment_is_active']:
                equipments_active.add(port_connection["equipment_id"])
            elif not port_connection['equipment_is_active']:
                equipments_is_not_active.add(port_connection["equipment_id"])
            else:
                raise ValidationError(message="Оборудование имеет неизестный тип")

    equipment_scheme.connection_active = list(equipments_active)
    equipment_scheme.connection_passive = list(equipments_is_not_active)
    equipment_scheme.save()

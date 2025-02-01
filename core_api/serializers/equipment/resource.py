from rest_framework import serializers

from models_app.models import Equipment
from typing import Dict, Union


class EquipmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    vlan_ip = serializers.JSONField(required=False)
    template = serializers.SerializerMethodField()
    free_ports = serializers.IntegerField()
    room_id = serializers.IntegerField(required=False)

    def get_template(self, obj: Equipment) -> Dict[str, Union[str, int]]:
        return {
            'manufacturer': obj.template.manufacturer.name if obj.template.manufacturer else None,
            'type': obj.template.type.name,
            'model': obj.template.model,
            'number_of_units': obj.template.number_of_units,
            'power': obj.template.power,
        }

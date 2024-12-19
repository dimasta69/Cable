from rest_framework import serializers

from models_app.models import Port


class EquipmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    vlan_ip = serializers.JSONField(required=False)
    template = serializers.SerializerMethodField()
    free_ports = serializers.IntegerField()
    room_id = serializers.IntegerField(required=False)

    @classmethod
    def get_template(cls, obj):
        return {
            'manufacturer': obj.template.manufacturer.name,
            'type': obj.template.type.name,
            'model': obj.template.model,
            'number_of_units': obj.template.number_of_units,
            'power': obj.template.power,
        }

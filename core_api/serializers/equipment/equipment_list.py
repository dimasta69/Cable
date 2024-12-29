from rest_framework import serializers

from core_api.serializers.room.room_list import RoomListSerializer
from models_app.models import Equipment


class EquipmentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    template = serializers.SerializerMethodField()
    free_ports = serializers.IntegerField()
    room = RoomListSerializer()

    @classmethod
    def get_template(cls, obj: Equipment):
        return {
            'manufacturer': obj.template.manufacturer.name if obj.template.manufacturer else None,
            'type': obj.template.type.name,
            'model': obj.template.model,
            'number_of_units': obj.template.number_of_units,
            'count_port': obj.template.count_port,
            'power': obj.template.power,
        }

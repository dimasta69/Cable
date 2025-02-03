from rest_framework import serializers

from core_api.serializers.room.resource import RoomListSerializer
from models_app.models import Equipment, VlanDevice
from typing import Dict, Union


class VlanDeviceSerializer(serializers.ModelSerializer):
    vlan_name = serializers.CharField(source="vlan__name")

    class Meta:
        model = VlanDevice
        fields = (
            "id",
            "vlan_name",
            "ip",
        )


class EquipmentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    template = serializers.SerializerMethodField()
    free_ports = serializers.IntegerField()
    room = RoomListSerializer()
    vlan = serializers.SerializerMethodField()

    def get_template(cls, obj: Equipment) -> Dict[str, Union[str, int, None]]:
        return {
            'manufacturer': obj.template.manufacturer.name if obj.template.manufacturer else None,
            'type': obj.template.type.name,
            'model': obj.template.model,
            'number_of_units': obj.template.number_of_units,
            'count_port': obj.template.count_port,
            'power': obj.template.power,
        }

    def get_vlan(self, obj: Equipment) -> VlanDeviceSerializer:
        return VlanDeviceSerializer(VlanDevice.objects.filter(object=obj), many=True).data

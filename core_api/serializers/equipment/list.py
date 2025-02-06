from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from models_app.models import Equipment, VlanDevice, Room
from typing import Dict, Union, List, Any


class VlanDeviceSerializer(serializers.ModelSerializer):
    vlan_name = serializers.CharField(source="vlan.name")

    class Meta:
        model = VlanDevice
        fields = (
            "id",
            "vlan_name",
            "ip",
        )


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
            "id",
            "number",
            "is_server_room",
            "floor",
        )


class EquipmentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    template = serializers.SerializerMethodField()
    free_ports = serializers.IntegerField()
    room = RoomSerializer()
    vlan = serializers.SerializerMethodField()

    def get_template(self, obj: Equipment) -> Dict[str, Union[str, int, None]]:
        return {
            'manufacturer': obj.template.manufacturer.name if obj.template.manufacturer else None,
            'type': obj.template.type.name,
            'model': obj.template.model,
            'number_of_units': obj.template.number_of_units,
            'count_port': obj.template.count_port,
            'power': obj.template.power,
        }

    def get_vlan(self, obj: Equipment) -> List[Dict[str, Any]]:
        vlan_devices = VlanDevice.objects.filter(
            device_id=obj.id, device_type=ContentType.objects.get_for_model(Equipment)
        ).select_related("vlan").order_by("vlan__name")
        return VlanDeviceSerializer(vlan_devices, many=True).data

from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from core_api.serializers.vlan.device.resource import VlanDeviceSerializer
from models_app.models import Port, Line, VlanDevice, PortMode
from core_api.serializers.port_template.resource import SpeedSerializer
from core_api.serializers.vlan.resource import VlanSerializer

from typing import Union, Dict, List

class PortModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortMode
        fields = (
            'id',
            'name',
            'red',
            'green',
            'blue',
            'alfa',
            'is_only_one_vlan',
        )

class LineSerializer(serializers.ModelSerializer):
    line_type = serializers.CharField(source="line_type.name", default=None)

    class Meta:
        model = Line
        fields = (
            "id",
            "line_type",
            "connection",
        )


class PortListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    uid = serializers.IntegerField(required=True)
    type = serializers.CharField(source="port_template.type_port.name", default=None)
    sfp = serializers.SerializerMethodField()
    speed = serializers.SerializerMethodField()
    line_type = serializers.CharField(source="line.line_type.name", default=None)
    vlan = serializers.SerializerMethodField()
    mac = serializers.CharField()
    front_side = serializers.IntegerField(source="front_side.id", default=None)
    back_side = serializers.IntegerField(source="back_side.id", default=None)
    line = LineSerializer()
    mode = PortModelSerializer()

    def get_speed(self, obj: Port) -> List[int]:
        return SpeedSerializer(obj.port_template.speed, many=True).data

    def get_sfp(self, obj: Port) -> Dict[str, Union[str, id, list[int]]]:
        if obj.sfp:
            return {
                'id': obj.sfp.id,
                'manufacturer': obj.sfp.manufacturer.name,
                'name': obj.sfp.name,
                'type_port': obj.sfp.type_port.name,
                'speed': obj.sfp.speed,
                'line_type': obj.sfp.line_type
            }
        else:
            return None

    def get_vlan(self, obj: Port) -> VlanSerializer:
        return VlanDeviceSerializer(
            VlanDevice.objects.filter(
                device_id=obj.id, device_type=ContentType.objects.get_for_model(Port)
            ), many=True
        ).data

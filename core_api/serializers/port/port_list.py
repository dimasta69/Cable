from rest_framework import serializers

from models_app.models import Port, Vlan, Line
from core_api.serializers.port_template.port_template_list import SpeedSerializer
from core_api.serializers.vlan.resource import VlanSerializer


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
    # ip = serializers.IPAddressField(default=None)
    mac = serializers.CharField()
    front_side = serializers.IntegerField(source="front_side.id", default=None)
    back_side = serializers.IntegerField(source="back_side.id", default=None)
    line = LineSerializer()

    def get_speed(self, obj: Port):
        return SpeedSerializer(obj.port_template.speed, many=True).data

    def get_sfp(self, obj: Port):
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

    def get_vlan(self, obj: Port):
        return (
            VlanSerializer(Vlan.objects.filter(device_type__model='port', device_id=obj.pk), many=True).data
        )

from rest_framework import serializers

from models_app.models import Port, Vlan
from core_api.serializers.port_template.port_template_list import SpeedSerializer
from core_api.serializers.vlan.resource import VlanSerializer


class LineSerializer(serializers.Serializer):
    line_type = serializers.CharField(source="line_type.name")
    connection = serializers.ListField()


class PortListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    uid = serializers.IntegerField(required=True)
    type = serializers.CharField(source="port_template.type_port.name")
    sfp = serializers.SerializerMethodField()
    speed = serializers.SerializerMethodField()
    line_type = serializers.CharField(source="line.line_type.name")
    vlan = serializers.SerializerMethodField()
    ip = serializers.IPAddressField()
    mac = serializers.CharField()
    line = LineSerializer(many=True)

    class Meta:
        model = Port
        fields = (
            "id",
            "uid",
            "line_type"
        )

    def get_speed(cls, obj: Port):
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

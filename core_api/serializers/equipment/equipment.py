from rest_framework import serializers

from models_app.models.port_template import PortTemplate
from models_app.models.port import Port


class EquipmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    vlan_ip = serializers.JSONField(required=False)
    template = serializers.SerializerMethodField()
    count_port = serializers.SerializerMethodField()
    free_ports = serializers.IntegerField()
    number_of_free_ports = serializers.SerializerMethodField()
    room_id = serializers.IntegerField(required=False)

    @classmethod
    def get_template(cls, obj):
        return {
            'manufacturer': obj.template.manufacturer.name,
            'type': obj.template.type,
            'model': obj.template.model,
            'number_of_units': obj.template.number_of_units,
            'power': obj.template.power,
        }

    @classmethod
    def get_count_port(cls, obj):
        return sum(PortTemplate.objects.filter(equipment_tmp=obj.template).values_list('count', flat=True))

    @classmethod
    def get_number_of_free_ports(cls, obj):
        free_ports = {}
        for port in PortTemplate.objects.filter(equipment_tmp=obj.template):
            free_ports[str(port.speed)] = (Port.objects.filter(equipment=obj, port_template=port, connection=None).
                                      count())
        return free_ports

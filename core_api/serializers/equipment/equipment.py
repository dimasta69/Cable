from rest_framework import serializers

from models_app.models import Port


class EquipmentSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    vlan_ip = serializers.JSONField(required=False)
    template = serializers.SerializerMethodField()
    count_port = serializers.IntegerField()
    free_ports = serializers.IntegerField()
    number_of_free_ports = serializers.SerializerMethodField()
    count_port_template_dict = serializers.JSONField()
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
    def get_number_of_free_ports(cls, obj):
        for port in obj.template.port_template.all():
            return {str(port.id): {
                str(port.speed): (Port.objects.filter(equipment=obj, port_template=port, connection=None).
                                  count()),}}

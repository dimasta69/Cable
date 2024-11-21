from rest_framework import serializers


class EquipmentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    vlan_ip = serializers.JSONField(required=False)
    template = serializers.SerializerMethodField()
    free_ports = serializers.IntegerField()

    @classmethod
    def get_template(cls, obj):
        return {
            'manufacturer': obj.template.manufacturer.name,
            'type': obj.template.type,
            'model': obj.template.model,
            'number_of_units': obj.template.number_of_units,
            'power': obj.template.power,
        }

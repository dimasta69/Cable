from rest_framework import serializers
from models_app.models.port.port_template.models import PortShip


class EquipmentTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.SerializerMethodField(required=False)
    type = serializers.SerializerMethodField(required=False)
    model = serializers.CharField(required=True)
    number_of_units = serializers.IntegerField(required=False)
    power = serializers.IntegerField(required=False)
    count_port = serializers.SerializerMethodField()

    def get_manufacturer(cls, obj):
        return {
            'id': obj.manufacturer.id,
            'name': obj.manufacturer.name,
        }

    def get_type(self, obj):
        return {
            "id": obj.type.id,
            "is_active": obj.type.is_active,
            "name": obj.type.name,
        }

    def get_count_port(cls, obj):
        return sum(PortShip.objects.filter(equipment_template=obj).values_list('count', flat=True))

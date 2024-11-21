from rest_framework import serializers
from models_app.models.port_template import PortTemplate


class EquipmentTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.SerializerMethodField(required=False)
    type = serializers.CharField(required=True)
    model = serializers.CharField(required=True)
    number_of_units = serializers.IntegerField(required=False)
    power = serializers.IntegerField(required=False)
    count_port = serializers.SerializerMethodField()

    @classmethod
    def get_manufacturer(cls, obj):
        return {
            'id': obj.manufacturer.id,
            'name': obj.manufacturer.name,
        }

    @classmethod
    def get_count_port(cls, obj):
        return sum(PortTemplate.objects.filter(equipment_tmp=obj.id).values_list('count', flat=True))

from rest_framework import serializers

from models_app.models import PortTemplate


class EquipmentTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.SerializerMethodField(required=False)
    type = serializers.CharField(required=True)
    model = serializers.CharField(required=False)
    count_port = serializers.SerializerMethodField()
    number_of_units = serializers.IntegerField(required=False)
    power = serializers.IntegerField(required=False)

    class Meta:
        ref = 'core_api_equipment_template_list_serializer'

    @classmethod
    def get_manufacturer(cls, obj):
        return {
            'id': obj.manufacturer.id,
            'name': obj.manufacturer.name,
        }

    @classmethod
    def get_count_port(cls, obj):
        return sum(PortTemplate.objects.filter(equipment_tmp=obj.id).values_list('count', flat=True))

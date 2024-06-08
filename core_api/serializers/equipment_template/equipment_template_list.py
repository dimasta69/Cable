from rest_framework import serializers


class EquipmentTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.SerializerMethodField(required=False)
    type = serializers.CharField(required=True)
    model = serializers.CharField(required=False)

    class Meta:
        ref = 'core_api_equipment_template_list_serializer'

    @classmethod
    def get_manufacturer(cls, obj):
        return {
            'id': obj.manufacturer.id,
            'name': obj.manufacturer.name,
        }

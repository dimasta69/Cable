from rest_framework import serializers


class PortTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    equipment_tmp = serializers.SerializerMethodField(required=False)
    count = serializers.IntegerField(required=True)

    class Meta:
        ref = 'core_api_port_template_list_serializer'

    @classmethod
    def get_equipment_tmp(cls, obj):
        return {
            'manufacturer': obj.equipment_tmp.manufacturer.name,
            'model': obj.equipment_tmp.model,
        }

from rest_framework import serializers


class SpeedSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    value = serializers.IntegerField(required=True)
    unit = serializers.CharField()


class PortTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    type_port = serializers.SerializerMethodField()
    speed = SpeedSerializer()
    count = serializers.IntegerField(required=True)
    modular = serializers.BooleanField(required=False)
    unit = serializers.ListField(child=serializers.IntegerField())
    lines = serializers.IntegerField(required=True)

    class Meta:
        ref = 'core_api_port_template_list_serializer'

    @classmethod
    def get_equipment_tmp(cls, obj):
        return {
            'manufacturer': obj.equipment_tmp.manufacturer.name,
            'model': obj.equipment_tmp.model,
        }

    @classmethod
    def get_type_port(cls, obj):
        if obj.type_port:
            return obj.type_port.name
        return None

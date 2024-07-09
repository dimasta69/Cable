from rest_framework import serializers


class SfpTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.SerializerMethodField()
    name = serializers.CharField()
    type_port = serializers.SerializerMethodField()
    speed = serializers.ListField()
    line_type = serializers.CharField()

    def get_manufacturer(self, obj):
        return obj.manufacturer.name

    def get_type_port(self, obj):
        return obj.type_port.name

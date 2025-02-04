from rest_framework import serializers
from core_api.serializers.speed.resource import SpeedListSerializer
from core_api.serializers.line_type.resource import LineTypeSerializer

class SfpTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.CharField(source="manufacturer.name")
    name = serializers.CharField()
    type_port = serializers.CharField(source="type_port.name")
    speed = SpeedListSerializer(many=True)
    line_type = LineTypeSerializer(many=True)

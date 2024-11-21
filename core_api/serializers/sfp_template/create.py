from rest_framework import serializers


class CreateSfpTemplateSerializer(serializers.Serializer):
    manufacturer_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    type_port_id = serializers.IntegerField(required=True)
    speed = serializers.ListField(required=True)
    line_type = serializers.CharField(required=True)

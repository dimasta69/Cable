from rest_framework import serializers



class SfpTemplateListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    manufacturer = serializers.CharField(source="manufacturer.name")
    name = serializers.CharField()
    type_port = serializers.CharField(source="type_port.name")
    speed = serializers.ListField()
    line_type = serializers.CharField()

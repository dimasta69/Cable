from rest_framework import serializers


class UpdatePortTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False)
    unit = serializers.ListField(child=serializers.IntegerField())
    lines = serializers.IntegerField(required=False)

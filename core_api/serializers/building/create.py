from rest_framework import serializers


class CreateBuildingSerializer(serializers.Serializer):
    scheme_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

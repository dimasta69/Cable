from rest_framework import serializers


class CreateBuildingSerializer(serializers.Serializer):
    scheme_id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=True)

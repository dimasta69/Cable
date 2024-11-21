from rest_framework import serializers


class UpdateBuildingSerializer(serializers.Serializer):
    number = serializers.CharField(required=False)
    coord_x = serializers.FloatField(required=False)
    coord_y = serializers.FloatField(required=False)

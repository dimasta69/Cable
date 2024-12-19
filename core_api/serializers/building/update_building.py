from rest_framework import serializers


class UpdateBuildingSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    coord_x = serializers.FloatField(required=False)
    coord_y = serializers.FloatField(required=False)

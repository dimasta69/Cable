from rest_framework import serializers


class BuildingListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    scheme_id = serializers.IntegerField(source='scheme.id')
    name = serializers.CharField(required=True)
    coord_x = serializers.FloatField(required=False)
    coord_y = serializers.FloatField(required=False)
    connection = serializers.ListField(required=False)

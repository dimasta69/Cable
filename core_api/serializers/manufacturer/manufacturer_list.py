from rest_framework import serializers


class ManufacturerListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        ref = 'core_api_manufacturer_list_serializer'

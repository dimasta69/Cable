from rest_framework import serializers


class CreateEquipmentTemplateSerializer(serializers.Serializer):
    manufacturer_id = serializers.IntegerField(required=False)
    type = serializers.CharField(required=True)
    model = serializers.CharField(required=True)
    number_of_units = serializers.IntegerField(required=False)
    power = serializers.IntegerField(required=False)
    count_port = serializers.SerializerMethodField()

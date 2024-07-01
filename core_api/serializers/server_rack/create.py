from rest_framework import serializers


class CreateServerRackSerializer(serializers.Serializer):
    number_of_units = serializers.IntegerField(required=True)
    room_id = serializers.IntegerField(required=True)
    title = serializers.CharField(required=False)
    max_power = serializers.IntegerField(required=False)

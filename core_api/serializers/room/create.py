from rest_framework import serializers


class CreateRoomSerializer(serializers.Serializer):
    building_id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=True)
    type = serializers.CharField(required=True)

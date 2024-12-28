from rest_framework import serializers


class CreateRoomSerializer(serializers.Serializer):
    building_id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=True)
    is_server_room = serializers.BooleanField(required=True)
    floor = serializers.IntegerField(required=False)

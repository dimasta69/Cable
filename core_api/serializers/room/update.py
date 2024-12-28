from rest_framework import serializers


class UpdateRoomSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=False)
    is_server_room = serializers.BooleanField(required=False)
    equipment_id = serializers.IntegerField(required=False)
    floor = serializers.IntegerField(required=False)

from rest_framework import serializers


class RoomListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=True)
    is_server_room = serializers.BooleanField(required=True)
    count_free_socket = serializers.IntegerField(required=False)

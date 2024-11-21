from rest_framework import serializers


class RoomListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=True)
    type = serializers.CharField(required=True)
    count_free_socket = serializers.IntegerField(required=False)

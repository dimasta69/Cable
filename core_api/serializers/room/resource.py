from rest_framework import serializers
from core_api.serializers.equipment.list import EquipmentListSerializer


class RoomListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number = serializers.CharField(required=True)
    is_server_room = serializers.BooleanField(required=True)
    equipments = EquipmentListSerializer(many=True, required=False)
    floor = serializers.IntegerField(required=False)

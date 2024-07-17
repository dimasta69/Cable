from rest_framework import serializers


class AddingToPortsSerializer(serializers.Serializer):
    port_list = serializers.ListField(child=serializers.IntegerField())
    equipment_id = serializers.IntegerField(required=True)

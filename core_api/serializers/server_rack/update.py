from rest_framework import serializers


class UpdateServerRackSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    max_power = serializers.IntegerField(required=False)
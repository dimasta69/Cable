from rest_framework import serializers


class ServerRackListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    number_of_units = serializers.IntegerField(required=True)
    title = serializers.CharField(required=False)
    max_power = serializers.IntegerField(required=False)
    free_power = serializers.IntegerField(required=False)
    free_units = serializers.IntegerField(required=False)

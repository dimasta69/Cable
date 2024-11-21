from rest_framework import serializers


class UpdatePortSerializer(serializers.Serializer):
    line_type = serializers.CharField(required=False)
    vlan_type = serializers.CharField(required=False)
    vlan = serializers.IntegerField(required=False)
    ip = serializers.IPAddressField(required=False)
    mac = serializers.CharField(required=False)
    connection_id = serializers.IntegerField(required=False)

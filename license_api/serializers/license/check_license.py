from rest_framework import serializers


class CheckLicenseSerializer(serializers.Serializer):
    period_end_date = serializers.CharField(required=False)
    time_unlimited = serializers.CharField(required=False)
    restriction_unlimited = serializers.CharField(required=False)
    restrictions = serializers.JSONField(required=False)
    cable_version = serializers.CharField(required=False)
    mac_id = serializers.CharField(required=True)
    restriction_remainder = serializers.ListSerializer(child=serializers.JSONField())
    time_remainder = serializers.CharField(required=False)

from rest_framework import serializers

from models_app.models import VlanDevice


class VlanDeviceSerializer(serializers.ModelSerializer):
    vlan = serializers.CharField(source="vlan.name")
    device_type = serializers.SerializerMethodField()

    def get_device_type(self, obj: VlanDevice) -> str:
        return obj.device_type.model

    class Meta:
        model = VlanDevice
        fields = (
            "id",
            "vlan",
            "ip",
            "device_type",
            "device_id",
        )

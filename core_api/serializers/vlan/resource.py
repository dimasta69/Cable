from rest_framework import serializers

from models_app.models import Vlan
from typing import Union, Dict


class VlanSerializer(serializers.ModelSerializer):
    segment = serializers.SerializerMethodField()

    def get_segment(self, obj: Vlan) -> Dict[str, Union[id, str]]:
        return {
            "id": str(obj.segment.id),
            "scheme_id": str(obj.segment.scheme.id),
            "name": str(obj.segment.name),
        }

    class Meta:
        model = Vlan
        fields = (
            "id",
            "name",
            "segment",
            "ip",
            "device_type",
            "device_id",
            "device",
        )

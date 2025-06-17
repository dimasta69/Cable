from rest_framework import serializers

from models_app.models import Vlan


class VlanSerializer(serializers.ModelSerializer):
    segment = serializers.CharField(source="segment.name")

    class Meta:
        model = Vlan
        fields = (
            "id",
            "name",
            "segment",
        )

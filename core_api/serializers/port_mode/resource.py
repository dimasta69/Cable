from rest_framework import serializers

from models_app.models import PortMode

class PortModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortMode
        fields = (
            "id",
            "name",
            "red",
            "green",
            "blue",
            "alfa",
            "is_only_one_vlan",
        )

from rest_framework import serializers

from models_app.models import PortShip


class PortShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortShip
        fields = (
            "id",
            "equipment_template",
            "port_template",
            "count",
            "unit",
            "lines",
        )

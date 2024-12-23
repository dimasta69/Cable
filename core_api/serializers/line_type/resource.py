from rest_framework import serializers

from models_app.models import LineType


class LineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineType
        fields = (
            "id",
            "name",
        )

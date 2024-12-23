from rest_framework import serializers

from models_app.models import Speed


class SpeedListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speed
        fields = (
            "id",
            "value"
        )

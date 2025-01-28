from rest_framework import serializers

from models_app.models import Segment

class SegmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Segment
        fields = (
            "id",
            "name",
        )

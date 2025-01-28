from rest_framework import serializers

from models_app.models import Segment

class SegmentSerializer(serializers.ModelSerializer):
    scheme_id = serializers.IntegerField(source="scheme.id")

    class Meta:
        model = Segment
        fields = (
            "id",
            "name",
            "scheme_id"
        )

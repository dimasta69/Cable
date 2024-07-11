from rest_framework import serializers


class AddSfpSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    sfp_template_id = serializers.IntegerField(required=True)

from rest_framework import serializers


class UpdateSfpTemplateSerializer(serializers.Serializer):
    speed = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        ref_name = 'core_api_update_sfp_template_serializer'

from rest_framework import serializers


class CreatePortTemplateSerializer(serializers.Serializer):
    equipment_tmp_id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=True)
    count = serializers.IntegerField(required=False)

    class Meta:
        ref = 'core_api_create_port_template'

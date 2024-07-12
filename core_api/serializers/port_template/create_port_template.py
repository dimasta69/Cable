from rest_framework import serializers


class CreatePortTemplateSerializer(serializers.Serializer):
    equipment_tmp_id = serializers.IntegerField(required=False)
    type_port_id = serializers.IntegerField(required=False)
    modular = serializers.BooleanField(required=False)
    name = serializers.CharField(required=True)
    speed = serializers.ListField(child=serializers.IntegerField())
    count = serializers.IntegerField(required=False)
    lines = serializers.IntegerField(required=True)
    unit = serializers.ListField(child=serializers.IntegerField(), required=True)

    class Meta:
        ref = 'core_api_create_port_template'

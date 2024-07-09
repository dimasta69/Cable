from rest_framework import serializers


class PortListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    uid = serializers.IntegerField(required=True)
    type = serializers.SerializerMethodField()
    speed = serializers.SerializerMethodField()
    line_type = serializers.CharField()
    vlan_type = serializers.CharField()
    vlan = serializers.IntegerField()
    ip = serializers.IPAddressField()
    mac = serializers.CharField()
    connection = serializers.SerializerMethodField()
    connection_pigtail = serializers.SerializerMethodField()

    @classmethod
    def get_speed(cls, obj):
        return obj.port_template.speed

    @classmethod
    def get_connection(cls, obj):
        if obj.connection:
            return {
                'id': obj.connection.id,
                'uid': obj.connection.uid,
                'ip': obj.connection.ip,
                'manufacturer': obj.connection.equipment.template.manufacturer.name,
                'type': obj.connection.equipment.template.type,
                'model': obj.connection.equipment.template.model,
            }
        return None

    @classmethod
    def get_connection_pigtail(cls, obj):
        if obj.connection_pigtail:
            return {
                'id': obj.connection_pigtail.id,
                'uid': obj.connection_pigtail.uid,
                'ip': obj.connection_pigtail.ip,
                'manufacturer': obj.connection_pigtail.equipment.template.manufacturer.name,
                'type': obj.connection_pigtail.equipment.template.type,
                'model': obj.connection_pigtail.equipment.template.model,
            }
        return None

    @classmethod
    def get_type(cls, obj):
        if obj.port_template.type_port:
            return {
                'name': obj.port_template.type_port.name,
                'modular': obj.port_template.modular,
            }
        return {
                'name': None,
                'modular': obj.port_template.modular
            }

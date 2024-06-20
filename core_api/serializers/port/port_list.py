from rest_framework import serializers


class PortListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    uid = serializers.IntegerField(required=True)
    sfp = serializers.SerializerMethodField()
    speed = serializers.SerializerMethodField()
    line_type = serializers.CharField()
    vlan_type = serializers.CharField()
    vlan = serializers.IntegerField()
    ip = serializers.IPAddressField()
    mac = serializers.CharField()
    connection = serializers.SerializerMethodField()

    @classmethod
    def get_sfp(cls, obj):
        return {
            'manufacturer': cls.sfp.manufacturer.name,
            'speed': cls.sfp.speed,
            'name': cls.sfp.name,
        }

    @classmethod
    def get_speed(cls, obj):
        return {
            obj.port_template.speed
        }

    @classmethod
    def get_connection(cls, obj):
        return {
            'id': obj.connection.id,
            'uid': obj.connection.uid,
            'ip': obj.connection.ip,
            'manufacturer': obj.connection.equipment.template.manufacturer.name,
            'type': obj.connection.equipment.template.type,
            'model': obj.connection.equipment.template.model,
        }
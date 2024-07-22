from rest_framework import serializers

from models_app.models.unit import Unit


class PortListSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    uid = serializers.IntegerField(required=True)
    type = serializers.SerializerMethodField()
    sfp = serializers.SerializerMethodField()
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
        connection = {}
        if obj.connection:
            if obj.connection.equipment.room:
                connection = {
                    'port':
                        {
                            'id': obj.connection.id,
                            'uid': obj.connection.uid,
                            'ip': obj.connection.ip,
                        },
                    'equipment':
                        {
                            'id': obj.connection.equipment.template.manufacturer.id,
                            'manufacturer': obj.connection.equipment.template.manufacturer.name or None,
                            'type': obj.connection.equipment.template.type,
                            'model': obj.connection.equipment.template.model,
                        },
                    'room':
                        {
                            'id': obj.connection.equipment.room.id,
                            'number': obj.connection.equipment.room.number
                        },
                    'building':
                        {
                            'id': obj.connection.equipment.room.building.id,
                            'number': obj.connection.equipment.room.building.number,
                        },
                }

            else:
                unit = Unit.objects.get(equipment=obj.connection.equipment)
                connection = {
                    'port':
                        {
                            'id': obj.connection.id,
                            'uid': obj.connection.uid,
                            'ip': obj.connection.ip,
                        },
                    'equipment':
                        {
                            'id': obj.connection.equipment.template.manufacturer.id,
                            'manufacturer': obj.connection.equipment.template.manufacturer.name or None,
                            'type': obj.connection.equipment.template.type,
                            'model': obj.connection.equipment.template.model,
                        },
                    'unit':
                        {
                            'id': unit.id,
                            'uid': unit.uid,
                            'side': unit.side,
                        },
                    'server_rack':
                        {
                            'id': unit.server_rack.id,
                            'title': unit.server_rack.title,
                        },
                    'room':
                        {
                            'id': unit.server_rack.room.id,
                            'number': unit.server_rack.room.number,
                        },
                    'building':
                        {
                            'id': unit.server_rack.room.building.id,
                            'number': unit.server_rack.room.building.number,
                        },
                }

        return connection

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

    def get_sfp(self, obj):
        if obj.sfp:
            return {
                'manufacturer': obj.sfp.manufacturer.name,
                'name': obj.sfp.name,
                'type_port': obj.sfp.type_port.name,
                'speed': obj.sfp.speed,
                'line_type': obj.sfp.line_type
            }

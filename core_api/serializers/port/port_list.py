from rest_framework import serializers

from models_app.models import Unit


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
                unit = (Unit.objects.filter(equipment=obj.connection.equipment)
                        .select_related('server_rack', 'server_rack__room', 'server_rack__room__building').first())
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
        connection = {}
        if obj.connection_pigtail:
            unit = (Unit.objects.filter(equipment=obj.connection_pigtail.equipment)
                    .select_related('server_rack', 'server_rack__room', 'server_rack__room__building').first())
            connection = {
                'port':
                    {
                        'id': obj.connection_pigtail.id,
                        'uid': obj.connection_pigtail.uid,
                        'ip': obj.connection_pigtail.ip,
                    },
                'equipment':
                    {
                        'id': obj.connection_pigtail.equipment.template.manufacturer.id,
                        'manufacturer': obj.connection_pigtail.equipment.template.manufacturer.name or None,
                        'type': obj.connection_pigtail.equipment.template.type,
                        'model': obj.connection_pigtail.equipment.template.model,
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
    def get_type(cls, obj):
        name = None
        if obj.port_template.type_port:
            name = obj.port_template.type_port.name
        return {
            'name': name,
            'modular': obj.port_template.modular
        }

    def get_sfp(self, obj):
        if obj.sfp:
            return {
                'id': obj.sfp.id,
                'manufacturer': obj.sfp.manufacturer.name,
                'name': obj.sfp.name,
                'type_port': obj.sfp.type_port.name,
                'speed': obj.sfp.speed,
                'line_type': obj.sfp.line_type
            }

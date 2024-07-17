from drf_yasg import openapi
from core_api.serializers.port.port_list import PortListSerializer


port_list = {
    'operation_description': 'Get port list',
    'tags': ['core_api/port'],
    'responses': {
        '200': openapi.Response(
            description='Success',
            examples={
                "id": 0,
                "uid": 0,
                "sfp": 'null',
                "type": {'name': 'test',
                         'modular': "bool"},
                'speed': [0, 1],
                'line_type': 'null',
                'vlan_type': 'null',
                'vlan': 'null',
                'ip': 'null',
                'mac': 'null',
                'connection': 'null'
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter(name='order_by',
                          in_=openapi.IN_QUERY,
                          description='Order photo by columns',
                          type=openapi.TYPE_STRING,
                          enum=['uid', '-uid', 'connection', '-connection', 'unit', '-unit']),
        openapi.Parameter(name='filter_equipment',
                          in_=openapi.IN_QUERY,
                          description='Search by manufacturer',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='filter_vlan',
                          in_=openapi.IN_QUERY,
                          description='Search by manufacturer',
                          type=openapi.TYPE_INTEGER),
    ]
}

update_port = {
    'operation_description': 'Update port',
    'tags': ['core_api/port'],
    'request_body': openapi.Schema(
        title='core_api_update_port',
        description='Update port',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            line_type=openapi.Schema(type=openapi.TYPE_STRING),
            vlan_type=openapi.Schema(type=openapi.TYPE_STRING),
            vlan=openapi.Schema(type=openapi.TYPE_INTEGER),
            ip=openapi.Schema(type=openapi.TYPE_INTEGER),
            mac=openapi.Schema(type=openapi.TYPE_STRING),
            connection_id=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
    ),
    'responses': {200: openapi.Response('Success', PortListSerializer)}
}

port_connection_pigtail = {
    'operation_description': 'Port connection pigtail',
    'tags': ['core_api/port'],
    'request_body': openapi.Schema(
        title='core_api_port_connection_pigtail',
        description='Update port',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            connection_pigtail_id=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
    ),
    'responses': {200: openapi.Response('Success', PortListSerializer)}
}

add_sfp = {
    'operation_description': 'Add sfp',
    'tags': ['core_api/port'],
    'request_body': openapi.Schema(
        title='core_api_port_add_sfp',
        description='Update port',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            sfp_template_id=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
    ),
    'responses': {200: openapi.Response('Success', PortListSerializer)}
}

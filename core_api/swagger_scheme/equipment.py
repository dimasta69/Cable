from drf_yasg import openapi

from core_api.serializers.equipment.equipment import EquipmentSerializer
from core_api.serializers.server_rack.server_rack import ServerRackSerializer

equipment_list = {
    'operation_description': 'Get equipment template list',
    'tags': ['core_api/equipment'],
    'responses': {
        '200': openapi.Response(
            description='Success',
            examples={
                "application/json": {
                    "pagination": {
                        "current_page": 0,
                        "per_page": 0,
                        "next_page": None,
                        "prev_page": None,
                        "total_pages": 0,
                        "total_count": 0
                    },
                    "results": [
                        {
                            'id': 0,
                            "vlan_ip": {
                                "2": "10.16.7.10"
                            },
                            'template':
                                {
                                    "manufacturer": "test",
                                    'type': 'test',
                                    'model': 'test',
                                    'number_of_units': 0,
                                    'power': 0,
                                },
                            'free_ports': 0,
                            'room': 0,
                        },
                    ]
                }
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter(name="page",
                          in_=openapi.IN_QUERY,
                          description='Page number',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='per_page',
                          in_=openapi.IN_QUERY,
                          description='Page size',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='order_by',
                          in_=openapi.IN_QUERY,
                          description='Order equipment by columns',
                          type=openapi.TYPE_STRING,
                          enum=['template__power', '-template__power', 'template__number_of_units',
                                '-template__number_of_units', 'template__count_port',
                                '-template__count_port', 'template__model', '-template__model',
                                'free_ports', '-free_ports']),
        openapi.Parameter(name='search_filter',
                          in_=openapi.IN_QUERY,
                          description='Search by symbols',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='filter_type',
                          in_=openapi.IN_QUERY,
                          description='Search by type',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='filter_manufacturer',
                          in_=openapi.IN_QUERY,
                          description='Search by manufacturer',
                          type=openapi.TYPE_STRING),
    ]
}

create_equipment = {
    'operation_description': 'Create equipment',
    'tags': ['core_api/equipment'],
    'request_body': openapi.Schema(
        title='core_api_create_equipment',
        description='Create equipment',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            equipment_template_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            vlan_ip=openapi.Schema(type=openapi.TYPE_STRING),
            unit_list_id=openapi.Schema(type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_INTEGER)),
            server_rack_id=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
        required=['equipment_template_id', 'unit_list_id', 'server_rack_id']
    ),
    'responses': {201: openapi.Response('Success', ServerRackSerializer)}
}

equipment = {
    'operation_description': 'Get equipment',
    'tags': ['core_api/equipment'],
    'responses': {200: openapi.Response('Success', EquipmentSerializer)}
}

delete_equipment = {
    'operation_description': 'Delete equipment template',
    'tags': ['core_api/equipment']
}

update_equipment = {
    'operation_description': 'Update equipment',
    'tags': ['core_api/equipment'],
    'request_body': openapi.Schema(
        title='core_api_equipment_update',
        description='Update equipment',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            vlan_ip=openapi.Schema(type=openapi.TYPE_STRING),
            room_id=openapi.Schema(type=openapi.TYPE_STRING),
        ),
    ),
    'responses': {200: openapi.Response('Success', EquipmentSerializer)}
}

add_equipment_for_unit = {
    'operation_description': 'Add equipment for unit',
    'tags': ['core_api/equipment'],
    'request_body': openapi.Schema(
        title='core_api_equipment_add_for_unit',
        description='Add equipment for equipment',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            unit_list_id=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER),
            ),
        ),
    ),
    'responses': {200: openapi.Response('Success', EquipmentSerializer)}
}

from drf_yasg import openapi

from core_api.serializers.server_rack.server_rack import ServerRackSerializer

server_rack_list = {
    'operation_description': 'Get server rack list',
    'tags': ['core_api/server_rack'],
    'responses': {
        '200': openapi.Response(
            description='Success',
            examples={
                "application/json": {
                    "id": 0,
                    'number_of_units': 0,
                    'title': 'Test',
                    'max_power': 0,
                    'free_power': 0,
                    'free_units': 0,
                }
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter(name='order_by',
                          in_=openapi.IN_QUERY,
                          description='Order by columns',
                          type=openapi.TYPE_STRING,
                          enum=['title', '-title', 'max_power', '-max_power', 'free_power',
                                '-free_power', 'free_units', '-free_units']),
        openapi.Parameter(name='filter_room_id',
                          in_=openapi.IN_QUERY,
                          description='Filter by room id',
                          type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter(name='search_filter',
                          in_=openapi.IN_QUERY,
                          description='Search by symbols',
                          type=openapi.TYPE_STRING),
    ]
}

create_server_rack = {
    'operation_description': 'Create server rack',
    'tags': ['core_api/server_rack'],
    'request_body': openapi.Schema(
        title='core_api_create_server_rack',
        description='Create server rack',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            number_of_units=openapi.Schema(type=openapi.TYPE_INTEGER),
            room_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            title=openapi.Schema(type=openapi.TYPE_STRING),
            max_power=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
        required=['number_of_units', 'room_id']
    ),
    'responses': {
        '201': openapi.Response(
            description='Success',
            examples={
                "application/json": {
                    "id": 0,
                    'number_of_units': 0,
                    'title': 'Test',
                    'max_power': 0,
                    'free_power': 0,
                    'free_units': 0,
                    'units': {
                        'uid': 0,
                        'side': 'Лицевая, Тыловая',
                        'equipment': {
                            'id': 0,
                            'manufacturer': 'test',
                            'type': "Серверная, Обычная",
                            'model': 'test',
                        },

                    },
                }
            }
        )
    },
}

delete_server_rack = {
    'operation_description': 'Delete server rack',
    'tags': ['core_api/server_rack']
}

update_server_rack = {
    'operation_description': 'Update server rack',
    'tags': ['core_api/server_rack'],
    'request_body': openapi.Schema(
        title='core_api_server_rack_update',
        description='Update server rack',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            number=openapi.Schema(type=openapi.TYPE_STRING),
            title=openapi.Schema(type=openapi.TYPE_STRING),
            max_power=openapi.Schema(type=openapi.TYPE_INTEGER),
        ),
    ),
    'responses': {
        '200': openapi.Response(
            description='Success',
            examples={
                "application/json": {
                    "id": 0,
                    'number_of_units': 0,
                    'title': 'Test',
                    'max_power': 0,
                    'free_power': 0,
                    'free_units': 0,
                    'units': {
                        'uid': 0,
                        'side': 'Лицевая, Тыловая',
                        'equipment': {
                            'id': 0,
                            'manufacturer': 'test',
                            'type': "Серверная, Обычная",
                            'model': 'test',
                        },

                    },
                }
            }
        )
    },
}

server_rack = {
    'operation_description': 'Get server rack',
    'tags': ['core_api/server_rack'],
    'responses': {
        '200': openapi.Response(
            description='Success',
            examples={
                "application/json": {
                    "id": 0,
                    'number_of_units': 0,
                    'title': 'Test',
                    'max_power': 0,
                    'free_power': 0,
                    'free_units': 0,
                    'units': {
                        'uid': 0,
                        'side': 'Лицевая, Тыловая',
                        'equipment': {
                            'id': 0,
                            'manufacturer': 'test',
                            'type': "Серверная, Обычная",
                            'model': 'test',
                        },

                    },
                }
            }
        )
    },
}

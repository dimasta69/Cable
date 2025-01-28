from drf_yasg import openapi

from core_api.serializers.access.resource import AccessListSerializer

access_list = {
    'operation_description': 'Get access list',
    'tags': ['core_api/access'],
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
                            "id": 0,
                            'user': {
                                'id': 0,
                                'username': 'username',
                            },
                            'role': 'Creator',
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
        openapi.Parameter(name='filter_role',
                          in_=openapi.IN_QUERY,
                          description='Filter by role',
                          type=openapi.TYPE_STRING,
                          enum=['Creator', 'Change', 'Read']),
        openapi.Parameter(name='filter_scheme_id',
                          in_=openapi.IN_QUERY,
                          description='Filter by scheme id',
                          type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter(name='search_filter',
                          in_=openapi.IN_QUERY,
                          description='Search by symbols',
                          type=openapi.TYPE_STRING),
    ]
}

create_access = {
    'operation_description': 'Create access',
    'tags': ['core_api/access'],
    'request_body': openapi.Schema(
        title='core_api_crate_access',
        description='Create access',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            scheme_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            user_id=openapi.Schema(type=openapi.TYPE_INTEGER),
            role=openapi.Schema(type=openapi.TYPE_STRING),
        ),
        required=['type', 'building_id', 'number']
    ),
    'responses': {201: openapi.Response('Success', AccessListSerializer)},
    'manual_parameters': [
        openapi.Parameter(name='role',
                          in_=openapi.IN_QUERY,
                          description='Role access',
                          type=openapi.TYPE_STRING,
                          enum=['Change', 'Read']),
    ]
}

delete_room = {
    'operation_description': 'Delete access',
    'tags': ['core_api/access']
}

update_access = {
    'operation_description': 'Update access',
    'tags': ['core_api/access'],
    'request_body': openapi.Schema(
        title='core_api_access_update',
        description='Update access',
        type=openapi.TYPE_OBJECT,
        properties=dict(
            role=openapi.Schema(type=openapi.TYPE_STRING),
        ),
        required=['role'],
    ),
    'responses': {200: openapi.Response('Success', AccessListSerializer)},
    'manual_parameters': [
        openapi.Parameter(name='role',
                          in_=openapi.IN_QUERY,
                          description='Role access',
                          type=openapi.TYPE_STRING,
                          enum=['Change', 'Read'])]
}

from drf_yasg import openapi

users_list = {
    'operation_description': "Get users list",
    'tags': ['core_api/users_list'],
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
                            "username": 'username'
                        },
                    ]
                }
            }
        )
    },
    'manual_parameters': [
        openapi.Parameter(name='page',
                          in_=openapi.IN_QUERY,
                          description='Page',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='per_page',
                          in_=openapi.IN_QUERY,
                          description='Per page',
                          type=openapi.TYPE_INTEGER),
        openapi.Parameter(name='order_by',
                          in_=openapi.IN_QUERY,
                          description='Order by username',
                          type=openapi.TYPE_STRING,
                          enum=['username', '-username']),
        openapi.Parameter(name='search_filter',
                          in_=openapi.IN_QUERY,
                          description='Search by username',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='scheme_id',
                          in_=openapi.IN_QUERY,
                          description='Scheme id',
                          type=openapi.TYPE_INTEGER,
                          required=True),
    ]
}

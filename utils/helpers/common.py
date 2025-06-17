from typing import Type

from rest_framework import serializers

from main_api.docs.base.serializers.pagination import PaginationSerializer


def add_pagination_to_data_serializer(
    data_serializer: Type[serializers.Serializer],
) -> Type[serializers.Serializer]:
    """Returns serializer combined of PaginationSerializer and
    given data serializer. Result represents the structure of a paginated response
    """

    class SwaggerPaginatedListSerializer(serializers.Serializer):
        pagination = PaginationSerializer(read_only=True)
        results = data_serializer(many=True, read_only=True)

        class Meta:
            ref_name = f"Paginated{data_serializer.__name__}"

    return SwaggerPaginatedListSerializer

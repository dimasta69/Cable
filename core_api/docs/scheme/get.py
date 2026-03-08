from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_parameters_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.scheme.resource import SchemeSerializer
from core_api.services.scheme.list import SchemeListService

RESPONSES: dict = {
    200: OpenApiResponse(
        description="OK",
        response=SchemeSerializer,
        examples=[
            OpenApiExample(
                name="OK",
                value=[
                    {
                        "id": 1,
                        "creator": {
                            "id": 1,
                            "username": "root",
                            "is_superuser": True
                        },
                        "title": "Scheme 1",
                        "count_user": 5,
                        "count_build": 3
                    }
                ],
            )
        ],
    ),
    400: OpenApiResponse(
        description="Bad Request",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Bad Request",
                value={
                    "type": "InvalidInputsError",
                    "message": "Invalid request data",
                    "translation_key": "invalid_request_data",
                    "debug_message": "null",
                    "details": {},
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ],
    ),
}

doc: DocsDict = {
    "tags": ["scheme"],
    "parameters": prepare_parameters_for_docs(SchemeListService, exclude=("current_user",)),
    "responses": RESPONSES,
}


from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import (
    prepare_parameters_for_docs, prepare_request_body_for_docs,
)

from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.access.resource import AccessListSerializer
from core_api.services.access.list import AccessListService

RESPONSES: dict = {
    200: OpenApiResponse(
        description="OK",
        response=AccessListSerializer,
        examples=[
            OpenApiExample(
                name="OK",
                value={
                    "id": 0,
                    "user": {
                        "id": "integer",
                        "username": "string",
                    },
                    "role": "string"
                },
            )
        ],
    ),
    400: OpenApiResponse(
        description="Bad Request",
        response={
            "type": "string",
            "message": "string",
            "translation_key": "string",
            "debug_message": "string",
            "details": {"string": [{"translation_key": "string", "message": "string"}]},
            "additional_info": {},
            "backtrace": [],
        },
        examples=[
            OpenApiExample(
                name="Bad Request (not all parameters have been passed)",
                description="Bad Request because not all parameters have been passed",
                value={
                    "type": "InvalidInputsError",
                    "message": "Invalid request data",
                    "translation_key": "invalid_request_data",
                    "debug_message": "null",
                    "details": {
                        "filter_scheme_id": [
                            {
                                "translation_key": "required",
                                "message": "This field is required."
                            }
                        ],
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ],
    ),
    403: OpenApiResponse(
        description="Access is not granted",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Access to the schema not granted",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "Access to the schema id {columns} is not granted",
                    "translation_key": "invalid",
                    "debug_message": "null",
                    "details": {
                        "current_user": [
                            {
                                "translation_key": "invalid",
                                "message": "Access to the schema id = 1 is not granted",
                            }
                        ]
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ]
    ),
    404: OpenApiResponse(
        description="Not Found",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Not Found",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "Not found {columns}}",
                    "translation_key": "not_found",
                    "debug_message": "null",
                    "details": {
                        "code": [
                            {
                                "translation_key": "not_found",
                                "message": "Code = string not found",
                            }
                        ]
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ],
    ),
}

doc: DocsDict = {
    "tags": ["access"],
    "parameters": prepare_parameters_for_docs(AccessListService, exclude=("current_user",), ),
    "responses": RESPONSES,
}

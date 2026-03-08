from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict

RESPONSES: dict = {
    204: OpenApiResponse(
        description="No Content",
        response=None,
    ),
    403: OpenApiResponse(
        description="Access is not granted",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Access to the schema not granted",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "Access to the schema is not granted",
                    "translation_key": "invalid",
                    "debug_message": "null",
                    "details": {
                        "current_user": [
                            {
                                "translation_key": "invalid",
                                "message": (
                                    "User access not allowed. "
                                    "Only the creator or administrator has access to delete"
                                ),
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
                    "message": "Not found",
                    "translation_key": "not_found",
                    "debug_message": "null",
                    "details": {
                        "id": [
                            {
                                "translation_key": "not_found",
                                "message": "Scheme id = 1 not found",
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
    "tags": ["scheme"],
    "responses": RESPONSES,
}


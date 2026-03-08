from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_request_body_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.sfp_template.resource import SfpTemplateListSerializer
from core_api.services.sfp_template.update import UpdateSfpTemplateService

RESPONSES: dict = {
    200: OpenApiResponse(
        description="OK",
        response=SfpTemplateListSerializer,
        examples=[
            OpenApiExample(
                name="OK",
                value={
                    "id": 1,
                    "manufacturer": "Cisco",
                    "name": "SFP-10G-LR",
                    "type_port": "SFP+",
                    "speed": [{"id": 1, "value": 10000}],
                    "line_type": [{"id": 1, "name": "Single-mode"}],
                },
            )
        ],
    ),
    400: OpenApiResponse(
        description="Bad Request",
        response=RESPONSE_FOR_ERROR,
    ),
    403: OpenApiResponse(
        description="User is not superuser",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Permission Denied",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "User is not superuser",
                    "translation_key": "invalid",
                    "debug_message": "null",
                    "details": {
                        "current_user": [
                            {
                                "translation_key": "invalid",
                                "message": "User is not superuser",
                            }
                        ]
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ],
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
                                "message": "Sfp template id=1 not found",
                            }
                        ]
                    },
                    "additional_info": {},
                    "backtrace": [],
                },
            ),
        ],
    ),
    422: OpenApiResponse(
        description="Template is used by ports",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Template in use",
                value={
                    "type": "ServiceObjectLogicError",
                    "message": "Невозможно изменить шаблон SFP: существуют порты, использующие этот шаблон.",
                    "translation_key": "not_found",
                    "debug_message": "null",
                    "details": {
                        "id": [
                            {
                                "translation_key": "not_found",
                                "message": "Невозможно изменить шаблон SFP: существуют порты, использующие этот шаблон.",
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
    "tags": ["sfp_template"],
    "request": prepare_request_body_for_docs(UpdateSfpTemplateService, exclude=("current_user", "id")),
    "responses": RESPONSES,
}

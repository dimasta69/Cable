from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_request_body_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.vlan.device.resource import VlanDeviceSerializer
from core_api.services.vlan_device.create import CreateVlanDeviceService

RESPONSES: dict = {
    201: OpenApiResponse(
        description="Created",
        response=VlanDeviceSerializer,
        examples=[
            OpenApiExample(
                name="Created",
                value={
                    "id": 1,
                    "vlan": "VLAN100",
                    "ip": "192.168.1.10",
                    "mask": "255.255.255.0",
                    "device_type": "port",
                    "device_id": 5,
                },
            )
        ],
    ),
    400: OpenApiResponse(
        description="Bad Request",
        response=RESPONSE_FOR_ERROR,
        examples=[
            OpenApiExample(
                name="Bad Request (validation)",
                value={
                    "type": "InvalidInputsError",
                    "message": "Invalid request data",
                    "translation_key": "invalid_request_data",
                    "debug_message": "null",
                    "details": {
                        "mask": [
                            {
                                "translation_key": "invalid",
                                "message": "Некорректная маска подсети или IP не относится к данной маске.",
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
    ),
    404: OpenApiResponse(
        description="Not Found",
        response=RESPONSE_FOR_ERROR,
    ),
}

doc: DocsDict = {
    "tags": ["vlan_device"],
    "request": prepare_request_body_for_docs(CreateVlanDeviceService, exclude=("current_user",)),
    "responses": RESPONSES,
    "description": (
        "Добавление VLAN на порт или оборудование. Можно указать ip и mask (маска подсети); "
        "при указании обоих проверяется совместимость IP и маски."
    ),
}

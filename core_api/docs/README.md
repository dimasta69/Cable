# Swagger Schema Documentation

Этот каталог содержит swagger схемы для всех роутеров API.

## Структура

Для каждого роутера создается папка в `core_api/docs/{router_name}/` с файлами:
- `get.py` - для GET запросов (список)
- `post.py` - для POST запросов (создание)
- `put.py` - для PUT запросов (обновление)
- `delete.py` - для DELETE запросов (удаление)
- `get_detail.py` - для GET запросов с ID (детали)
- `patch_*.py` - для PATCH запросов (если есть)

## Шаблон создания схемы

### GET запрос (список)

```python
from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from utils.helpers.auto_parameters_spectacular import prepare_parameters_for_docs
from utils.drf_spectacular_constants.response_for_error import RESPONSE_FOR_ERROR
from utils.types import DocsDict
from core_api.serializers.{module}.resource import {Module}Serializer
from core_api.services.{module}.list import {Module}ListService

RESPONSES: dict = {
    200: OpenApiResponse(
        description="OK",
        response={Module}Serializer,
        examples=[...],
    ),
    400: OpenApiResponse(...),
    403: OpenApiResponse(...),
    404: OpenApiResponse(...),
}

doc: DocsDict = {
    "tags": ["{module}"],
    "parameters": prepare_parameters_for_docs({Module}ListService, exclude=("current_user",)),
    "responses": RESPONSES,
}
```

### POST запрос (создание)

```python
from utils.helpers.auto_parameters_spectacular import prepare_request_body_for_docs
from core_api.services.{module}.create import Create{Module}Service

doc: DocsDict = {
    "tags": ["{module}"],
    "request": prepare_request_body_for_docs(Create{Module}Service, exclude=("current_user",)),
    "responses": RESPONSES,
}
```

### PUT запрос (обновление)

```python
from core_api.services.{module}.update import Update{Module}Service

doc: DocsDict = {
    "tags": ["{module}"],
    "request": prepare_request_body_for_docs(Update{Module}Service, exclude=("current_user", "id")),
    "responses": RESPONSES,
}
```

### DELETE запрос

```python
doc: DocsDict = {
    "tags": ["{module}"],
    "responses": RESPONSES,
}
```

## Использование в views

После создания схемы, добавьте декораторы в views:

```python
from drf_spectacular.utils import extend_schema
from core_api.docs.{module}.get import doc as {module}_get_doc
from core_api.docs.{module}.post import doc as {module}_post_doc

class {Module}ListView(APIView):
    @extend_schema(**{module}_get_doc)
    def get(self, request):
        ...

    @extend_schema(**{module}_post_doc)
    def post(self, request):
        ...
```

## Роутеры, для которых нужно создать схемы

- [x] scheme
- [x] equipment
- [x] building
- [ ] room
- [ ] port
- [ ] manufacturer
- [ ] equipment_template
- [ ] equipment_type
- [ ] port_template
- [ ] port_mode
- [ ] type_port
- [ ] speed
- [ ] line_type
- [ ] server_rack
- [ ] sfp_template
- [ ] segment
- [ ] vlan
- [x] vlan_device (post, patch)
- [ ] map
- [ ] access (уже есть)
- [ ] users_list
- [ ] connection
- [ ] disconnection
- [ ] connection_port_ship
- [ ] figure

## Важные замечания

1. Всегда исключайте `current_user` из параметров/тела запроса
2. Для path параметров (например, `id`) используйте `path_parameters=("id",)` в `prepare_parameters_for_docs`
3. Используйте соответствующие сериализаторы для responses
4. Добавьте стандартные ответы: 200/201, 400, 403, 404, 422 (если нужно)
5. Используйте `RESPONSE_FOR_ERROR` для ошибок


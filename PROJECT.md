# Cable — документация проекта

## Описание

**Cable** — веб-приложение для ведения кабельного журнала (учёт сетевой инфраструктуры). Система хранит данные о зданиях, помещениях, оборудовании, портах, схемах соединений, VLAN и связанных сущностях. Включает лицензирование и REST API с JWT-аутентификацией.

---

## Технологический стек

| Категория | Технологии |
|-----------|------------|
| Backend | Django 5.x, Django REST Framework |
| БД | PostgreSQL (psycopg2/psycopg) |
| Аутентификация | JWT (rest-framework-simplejwt), Djoser |
| Документация API | drf-spectacular (OpenAPI, Swagger UI, ReDoc) |
| Очереди/кэш | Celery, Redis (django-redis) |
| Сервер | Gunicorn |
| Инфраструктура | Docker, docker-compose, Nginx |
| Качество кода | pre-commit: black, isort, flake8, mypy, bandit, pyupgrade, autoflake, pydocstringformatter |

---

## Структура проекта

```
Cable/
├── cabel/                    # Конфигурация Django-проекта
│   ├── settings/             # Настройки (django, database, auth, jwt, celery, cache, cors, rest_framework)
│   ├── urls.py               # Корневые URL: admin, core_api, license_api
│   ├── views.py              # Главная страница (index)
│   └── wsgi.py
├── core_api/                 # Основное REST API
│   ├── docs/                 # Swagger-схемы для drf-spectacular (building, equipment, scheme, access, …)
│   ├── serializers/          # Сериализаторы по ресурсам
│   ├── services/             # Бизнес-логика (Service-объекты: list, create, update, delete, …)
│   ├── urls/                 # Маршруты API (auth, scheme, equipment, building, room, port, map, vlan, …)
│   └── views/                # APIView-классы по ресурсам
├── license_api/              # API лицензирования
│   ├── middleware/           # Проверка лицензии и времени (check_license, check_time)
│   ├── serializers/
│   ├── services/             # Загрузка/проверка лицензии, MAC
│   ├── urls/                 # license, mac
│   └── views/
├── models_app/               # Модели и админка
│   ├── admin/                # Регистрация моделей в Django Admin по доменам
│   ├── migrations/
│   └── models/               # User, Scheme, Building, Room, Equipment, Port, Vlan, Map, Figure, …
├── utils/                    # Общие утилиты
│   ├── license/              # Лицензирование (license_manager, exception, generete_mac_based_id)
│   ├── drf_spectacular_constants/  # Константы для документации (ошибки и т.д.)
│   ├── helpers/              # auto_parameters_spectacular, common
│   ├── errors.py             # Ошибки валидации
│   ├── exception_handler.py  # Обработчик исключений DRF
│   ├── pagination.py
│   ├── services.py           # Базовый Service (django-service-objects-подобная логика), ServiceOutcome
│   └── types.py              # Типы (DocsDict и др.)
├── create_superuser.py       # Скрипт создания суперпользователя
├── manage.py
├── Dockerfile                # Python 3.11, Pipenv, migrate + test + superuser + collectstatic + gunicorn
├── docker-compose.yml        # postgres, web, front, nginx
├── Pipfile / Pipfile.lock     # Зависимости (Python 3.11)
├── .pre-commit-config.yaml   # Хуки: black, isort, flake8, mypy, bandit, …
└── .github/workflows/        # CI/CD: деплой по push в testing (SSH + docker-compose)
```

---

## Модели данных (кратко)

- **User** — пользователи.
- **Unit** — единицы (в контексте оборудования/портов).
- **Scheme** — схема (проект); привязана к создателю, считаются здания и пользователи.
- **Building** — здание (в рамках схемы).
- **Room** — комната (в здании).
- **ServerRack** — серверная стойка.
- **Manufacturer** — производитель.
- **EquipmentTemplate** / **EquipmentTemplateType** — шаблон оборудования и его тип.
- **Equipment** — экземпляр оборудования (шаблон, комната, схема, свободные порты, связи equipment–equipment).
- **Port**, **PortTemplate**, **PortMode**, **TypePort**, **PortShip** — порты и их шаблоны/режимы/типы.
- **Line**, **LineType** — линии и типы линий.
- **Speed** — скорость.
- **SfpTemplate** — шаблон SFP.
- **Segment** — сетевой сегмент.
- **Vlan**, **VlanDevice** — VLAN и привязка к устройству (ContentType).
- **Access** — доступ к объектам (ContentType + object_id).
- **SchemeMap**, **EquipmentScheme**, **Figure** — карта схемы, оборудование на карте, фигуры.

Общая база: **BaseModel** (created_at, updated_at, full_clean в save) + миксины (например, ShowModelInfoMixin).

---

## API

### Точки входа

- **Core API**: префикс `core_api/` (в `cabel/urls.py`).
- **License API**: префикс `license_api/`.
- **Документация**: `core_api/api/schema/`, `core_api/api/docs/` (Swagger), `core_api/api/schema/redoc/` (ReDoc).

### Основные разделы Core API

| Префикс | Назначение |
|---------|------------|
| `auth/` | Аутентификация (Djoser, JWT) |
| `scheme/` | Схемы |
| `building/` | Здания |
| `room/` | Комнаты |
| `equipment/` | Оборудование |
| `equipment_template/`, `equipment_type/` | Шаблоны и типы оборудования |
| `port/` | Порты, подключения, отключения, SFP |
| `port_template/`, `type_port/`, `port_mode/` | Шаблоны и типы портов |
| `manufacturer/` | Производители |
| `server_rack/` | Стойки |
| `sfp_template/` | Шаблоны SFP |
| `access/` | Доступы |
| `users_list/` | Список пользователей |
| `connection/`, `disconnection/`, `connection_port_ship/` | Соединения и отключения |
| `speed/`, `line_type/` | Скорости и типы линий |
| `map/` | Карты схем |
| `segment/` | Сегменты |
| `vlan/`, `vlan_device/` | VLAN и устройства |
| `figure/` | Фигуры на карте |

### Паттерн View + Service

- **Views**: тонкие `APIView`, вызывают сервисы через `ServiceOutcome(SomeService, request.data | kwargs | {'current_user': request.user})`.
- **Сервисы**: наследуют базовый `Service` из `utils.services`, объявляют поля (как у Form), реализуют `process()`; используются для list/create/update/delete и специализированных операций (например, connection, disconnect, refresh).
- **Документация**: в `core_api/docs/{resource}/` — модули `get`, `post`, `put`, `delete`, при необходимости `get_detail`, `patch_*`; подключаются через `extend_schema` в view. Подробнее — в `core_api/docs/README.md`.

### Лицензирование

- **License API**: загрузка/проверка лицензии, работа с MAC.
- **Middleware**: для запросов POST/PUT/PATCH проверяется наличие и валидность файла лицензии (срок, MAC, лимиты и т.д.); при ошибке выбрасываются исключения из `utils.license.exception`.

---

## Настройка и запуск

### Переменные окружения (.env)

Пример (как в корневом README):

```env
DB_NAME=Cabel
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432
```

Для продакшена/CI могут использоваться также `DEBUG`, переменные для JWT, Redis, Celery и т.д.

### Локально

1. Установить зависимости: `pipenv install` (при необходимости `pipenv install --dev`).
2. Создать и применить миграции: `python manage.py migrate`.
3. При необходимости создать суперпользователя: `python create_superuser.py --noinput` или через `manage.py createsuperuser`.
4. Запуск: `python manage.py runserver` или через Gunicorn.

### Docker

- **БД**: сервис `postgres` (порт 5435:5432), данные в volume `pg_dump`.
- **Backend**: сервис `web` (порт 8000), в Dockerfile — migrate, test, create_superuser, collectstatic, gunicorn на 0.0.0.0:8000.
- **Frontend**: сервис `front` (сборка из другого контекста `/opt/www/cs/cable_journal`), порт 3000.
- **Nginx**: порт 80, статика и прокси к front/web.

Запуск: `docker-compose up -d` (при необходимости `docker-compose up -d --build web`).

---

## Разработка и качество кода

- **pre-commit**: при коммите запускаются проверки (в т.ч. black, isort, flake8, mypy с исключением миграций, bandit, pyupgrade, autoflake, pydocstringformatter). Конфиг: `.pre-commit-config.yaml`.
- **Тесты**: в Dockerfile перед стартом приложения выполняется `python manage.py test`; тесты находятся в проекте (например, с factory-boy в dev-зависимостях).
- **CI/CD**: при push в ветку `testing` выполняется workflow (checkout, SSH на сервер, git pull, пересборка и перезапуск контейнера `web`). Секреты: `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`, `PROJECT_FOLDER`.

---

## Документация API (Swagger)

- Схемы для роутеров лежат в `core_api/docs/{router_name}/` (get, post, put, delete, при необходимости get_detail, patch_*).
- Используются утилиты из `utils.helpers.auto_parameters_spectacular` и константы из `utils.drf_spectacular_constants.response_for_error`.
- В `core_api/docs/README.md` перечислены роутеры, для которых схемы уже созданы (scheme, equipment, building, access) и те, для которых ещё нужно добавить описание (room, port, manufacturer, map, vlan, connection, figure и др.).

---

## Краткое резюме

Cable — это Django REST API для кабельного журнала с богатой доменной моделью (схемы, здания, комнаты, оборудование, порты, соединения, VLAN, карты). Используются сервисный слой (Service + ServiceOutcome), JWT, лицензирование через middleware, drf-spectacular для OpenAPI/Swagger, Docker и CI/CD на GitHub Actions. Документация по добавлению новых схем API сосредоточена в `core_api/docs/README.md`.

## Логика работы приложения
- Сервис connection. Нужен для подключения между собой портов. Есть массив, в котором содержаться id портов, они находятся в том проядке, что и подключены между собой. Если это патч-панель (пассиваня), то они идут друг за другом как подключенные. Линии можно соединять между собой, но только те, которые не подключены (соотвественно начало или конец списка).
- В `core_api.utils.connection` линия представлена как **односвязный список портов**: порядок задаётся связями `Port.front_side` (от головы к хвосту). При создании линии список `Line.connection` собирается обходом от головы (`get_chain_head` → `ports_from_head`); при разрыве используются сохранённые массивы.

## Правила подлкючения портов
- Нельзя подключать порты с разной скоростью, видом передачи данных (одномодовый, многомодовый, ethernet кабель и тд.). Если у нас оборудование предусматривает подлкючение в нее sfp модулей, то так же проверка между ими.  
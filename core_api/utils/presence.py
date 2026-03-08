"""
Унифицированная проверка наличия объекта по ID в сервисах.

Вариант 1 — один метод на все проверки (предпочтительно):

  class DeleteBuildingService(PresenceChecksMixin, ResourceAccessMixin, ServiceWithResult):
      custom_validations = ["run_presence_checks", "access_presence"]

      presence_checks = [
          ("_building", "id", "Building"),
      ]

  # Опциональный фильтр (проверять только если поле передано):
  presence_checks = [
          ("_building", "filter_building_id", "Building", True),  # only_if_set=True
      ]
  # Или словарём:
  presence_checks = [
          {"obj_attr": "_building", "field_name": "id", "model_label": "Building"},
          {"obj_attr": "_room", "field_name": "room_id", "model_label": "Room", "error_field": "room_id"},
      ]

Вариант 2 — вручную вызывать check_presence в отдельных методах (если нужна особая логика).
"""

from rest_framework import status
from rest_framework.exceptions import NotFound


def _parse_presence_spec(spec):
    """Преобразует элемент presence_checks в единый dict."""
    if isinstance(spec, dict):
        return spec
    # (obj_attr, field_name, model_label) или (..., only_if_set)
    obj_attr, field_name, model_label = spec[0], spec[1], spec[2]
    out = {"obj_attr": obj_attr, "field_name": field_name, "model_label": model_label}
    if len(spec) >= 4:
        out["only_if_set"] = spec[3]
    return out


def check_presence(
    service,
    obj,
    *,
    field_name: str,
    model_label: str,
    error_field: str | None = None,
    only_if_set: bool = False,
) -> None:
    """
    Добавить ошибку 404 в сервис, если объект не найден (obj is None).

    :param service: экземпляр сервиса (ServiceWithResult), у которого вызываются add_error и response_status
    :param obj: объект модели или None (обычно свойство сервиса вроде self._building)
    :param field_name: имя поля в cleaned_data для текста ошибки (например 'id', 'filter_building_id')
    :param model_label: человекочитаемое имя модели для сообщения (например 'Building', 'Room')
    :param error_field: поле формы для привязки ошибки; по умолчанию совпадает с field_name
    :param only_if_set: если True, проверка выполняется только когда service.cleaned_data[field_name] задано
    """
    if only_if_set and not service.cleaned_data.get(field_name):
        return
    if obj is not None:
        return
    field_for_error = error_field if error_field is not None else field_name
    value = service.cleaned_data.get(field_name, '')
    service.add_error(
        field_for_error,
        NotFound(f"{model_label} id={value} not found"),
    )
    service.response_status = status.HTTP_404_NOT_FOUND


class PresenceChecksMixin:
    """
    Миксин для сервиса: один метод run_presence_checks выполняет все проверки из presence_checks.

    В custom_validations укажите "run_presence_checks" вместо отдельных xxx_presence.

    presence_checks — список спецификаций. Каждая запись:
    - кортеж: (obj_attr, field_name, model_label) или (obj_attr, field_name, model_label, only_if_set);
    - или dict: obj_attr, field_name, model_label [, error_field] [, only_if_set].
    obj_attr — имя атрибута сервиса с объектом (например "_building").
    """

    presence_checks = []

    def run_presence_checks(self) -> None:
        for spec in getattr(self.__class__, "presence_checks", []):
            p = _parse_presence_spec(spec)
            obj = getattr(self, p["obj_attr"])
            check_presence(
                self,
                obj,
                field_name=p["field_name"],
                model_label=p["model_label"],
                error_field=p.get("error_field"),
                only_if_set=p.get("only_if_set", False),
            )

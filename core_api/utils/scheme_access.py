"""
Миксины для проверки доступа в сервисах без дублирования кода.

Использование в сервисе:
  1. Наследовать Service от ResourceAccessMixin (перед ServiceWithResult).
  2. Добавить 'access_presence' в custom_validations.
  3. Реализовать get_access_scope(self) -> dict | None (None — проверка не выполняется).
  4. При необходимости задать access_required_roles (по умолчанию Change/Creator).

Пример:

  class DeleteBuildingService(ResourceAccessMixin, ServiceWithResult):
      custom_validations = ["building_presence", "access_presence"]

      access_required_roles = AccessChecker.ROLES_CHANGE

      def get_access_scope(self):
          return scope_for_building(self._building)

      @property
      def _building(self): ...
"""

from django.core.exceptions import PermissionDenied

from rest_framework import status

from core_api.utils.access_checker import AccessChecker


class ResourceAccessMixin:
    """
    Миксин проверки доступа по иерархии Access.
    Сервис должен реализовать get_access_scope() -> dict | None.
    """

    access_required_roles = AccessChecker.ROLES_CHANGE

    def get_access_scope(self):
        """
        Вернуть scope для проверки доступа или None (проверка не выполняется).
        Переопределяется в сервисе.
        """
        return None

    def access_presence(self) -> None:
        scope = self.get_access_scope()
        if scope is None:
            return
        user = self.cleaned_data.get('current_user')
        if not AccessChecker.has_permission(user, self.access_required_roles, scope):
            scheme_id = scope.get('scheme_id', '')
            self.add_error(
                'current_user',
                PermissionDenied(
                    f'Access to the schema id = {scheme_id} is not granted'
                ),
            )
            self.response_status = status.HTTP_403_FORBIDDEN


class SchemeAccessMixin(ResourceAccessMixin):
    """
    Упрощённый миксин для ресурсов, привязанных только к схеме.
    Сервис реализует _get_scheme_id_for_access(self) -> int | None.
    """

    def get_access_scope(self):
        from core_api.utils.access_checker import scope_for_scheme_id

        scheme_id = getattr(self, '_get_scheme_id_for_access', lambda: None)()
        return scope_for_scheme_id(scheme_id)

"""
Централизованная проверка доступа по иерархии Access (Scheme → Building → Room → ServerRack).

Использование:
  from core_api.utils.access_checker import AccessChecker, scope_for_building

  scope = scope_for_building(building)
  if not AccessChecker.has_permission(user, ['Change', 'Creator'], scope):
      raise PermissionDenied(...)
"""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from models_app.models import Access, Scheme, Building, Room, ServerRack, Segment, Vlan


class AccessChecker:
    """
    Проверка прав пользователя по иерархии ресурсов.
    Суперпользователь всегда имеет доступ.
    """

    ROLES_READ = ['Read', 'Change', 'Creator']
    ROLES_CHANGE = ['Change', 'Creator']

    @classmethod
    def has_permission(cls, user, required_roles, scope):
        """
        Проверяет, есть ли у user доступ с одной из ролей required_roles
        к любому из объектов в scope.

        :param user: User
        :param required_roles: список ролей, напр. ['Change', 'Creator'] или ['Read', 'Change', 'Creator']
        :param scope: dict с ключами scheme_id, building_id, room_id, server_rack_id (достаточно переданных)
        :return: bool
        """
        if not user or getattr(user, 'is_superuser', False):
            return True
        if not scope or not required_roles:
            return False

        scope_conditions = []
        if scope.get('scheme_id') is not None:
            ct_scheme = ContentType.objects.get_for_model(Scheme)
            scope_conditions.append(Q(object_type=ct_scheme, object_id=scope['scheme_id']))
        if scope.get('building_id') is not None:
            ct_building = ContentType.objects.get_for_model(Building)
            scope_conditions.append(Q(object_type=ct_building, object_id=scope['building_id']))
        if scope.get('room_id') is not None:
            ct_room = ContentType.objects.get_for_model(Room)
            scope_conditions.append(Q(object_type=ct_room, object_id=scope['room_id']))
        if scope.get('server_rack_id') is not None:
            ct_rack = ContentType.objects.get_for_model(ServerRack)
            scope_conditions.append(Q(object_type=ct_rack, object_id=scope['server_rack_id']))
        if scope.get('segment_id') is not None:
            ct_segment = ContentType.objects.get_for_model(Segment)
            scope_conditions.append(Q(object_type=ct_segment, object_id=scope['segment_id']))
        if scope.get('vlan_id') is not None:
            ct_vlan = ContentType.objects.get_for_model(Vlan)
            scope_conditions.append(Q(object_type=ct_vlan, object_id=scope['vlan_id']))

        if not scope_conditions:
            return False

        scope_or = scope_conditions[0]
        for c in scope_conditions[1:]:
            scope_or |= c
        q = Q(user=user, role__in=required_roles) & scope_or
        return Access.objects.filter(q).exists()

    @classmethod
    def has_permission_to_any_vlan_in_segment(cls, user, segment, required_roles):
        """Проверяет, есть ли у user доступ к любому VLAN в segment (по записям Access на VLAN)."""
        if not user or getattr(user, 'is_superuser', False):
            return True
        if not segment or not required_roles:
            return False
        ct_vlan = ContentType.objects.get_for_model(Vlan)
        vlan_ids = list(segment.vlans.values_list('pk', flat=True))
        if not vlan_ids:
            return False
        return Access.objects.filter(
            user=user,
            role__in=required_roles,
            object_type=ct_vlan,
            object_id__in=vlan_ids,
        ).exists()


def scope_for_scheme(scheme):
    """Scope для доступа к схеме."""
    if scheme is None:
        return None
    return {'scheme_id': scheme.pk}


def scope_for_scheme_id(scheme_id):
    """Scope по id схемы (без загрузки объекта из БД)."""
    if scheme_id is None:
        return None
    return {'scheme_id': scheme_id}


def scope_for_building(building):
    """Scope для доступа к зданию и его содержимому (схема + здание)."""
    if building is None:
        return None
    return {
        'scheme_id': building.scheme_id,
        'building_id': building.pk,
    }


def scope_for_room(room):
    """Scope для доступа к комнате (схема, здание, комната)."""
    if room is None:
        return None
    return {
        'scheme_id': room.building.scheme_id,
        'building_id': room.building_id,
        'room_id': room.pk,
    }


def scope_for_server_rack(server_rack):
    """Scope для доступа к стойке (схема, здание, комната, стойка)."""
    if server_rack is None:
        return None
    return {
        'scheme_id': server_rack.room.building.scheme_id,
        'building_id': server_rack.room.building_id,
        'room_id': server_rack.room_id,
        'server_rack_id': server_rack.pk,
    }


def scope_for_equipment(equipment):
    """
    Scope для доступа к оборудованию.
    Учитывает размещение: в комнате или в стойке.
    Оборудование должно быть загружено с select_related('room', 'room__building')
    и prefetch_related('units__server_rack__room__building') при размещении в стойке.
    """
    if equipment is None:
        return None
    scope = {'scheme_id': equipment.scheme_id}
    if getattr(equipment, 'room_id', None) is not None and getattr(equipment, 'room', None):
        scope['building_id'] = equipment.room.building_id
        scope['room_id'] = equipment.room_id
    else:
        unit = equipment.units.first() if hasattr(equipment, 'units') else None
        if unit and getattr(unit, 'server_rack_id', None):
            scope['building_id'] = unit.server_rack.room.building_id
            scope['room_id'] = unit.server_rack.room_id
            scope['server_rack_id'] = unit.server_rack_id
    return scope


def scope_for_segment(segment):
    """Scope для доступа к сегменту (схема + сегмент)."""
    if segment is None:
        return None
    return {'scheme_id': segment.scheme_id, 'segment_id': segment.pk}


def scope_for_map(scheme_map):
    """Scope для доступа к карте схемы (проверка по схеме)."""
    if scheme_map is None:
        return None
    return scope_for_scheme_id(getattr(scheme_map, 'scheme_id', None))


def scope_for_vlan(vlan):
    """Scope для доступа к VLAN (схема, сегмент, vlan)."""
    if vlan is None:
        return None
    return {
        'scheme_id': vlan.segment.scheme_id,
        'segment_id': vlan.segment_id,
        'vlan_id': vlan.pk,
    }

from django import forms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from functools import lru_cache

from rest_framework import status

from models_app.models import Scheme
from utils.services import ServiceWithResult
from utils.fields import ModelField
from models_app.models import Equipment, EquipmentTemplate, User, Access, Building, Room, ServerRack


class CreateEquipmentService(ServiceWithResult):
    equipment_template_id = forms.IntegerField(required=True)
    scheme_id = forms.IntegerField(required=True)
    current_user = ModelField(User)

    scheme_content_type = ContentType.objects.get_for_model(Scheme)
    building_content_type = ContentType.objects.get_for_model(Building)
    room_content_type = ContentType.objects.get_for_model(Room)
    server_rack_content_type = ContentType.objects.get_for_model(ServerRack)

    custom_validations = ["equipment_template_presence", "scheme_presence", "access_presence"]

    def process(self):
        self.run_custom_validations()
        if self.is_valid():
            self.result = self._create_equipment
        return self

    @property
    def _create_equipment(self) -> Equipment:
        return Equipment.objects.create(template=self._equipment_template, scheme=self._scheme)

    @property
    @lru_cache()
    def _equipment_template(self) -> Equipment | None:
        try:
            return EquipmentTemplate.objects.get(id=self.cleaned_data['equipment_template_id'])
        except EquipmentTemplate.DoesNotExist:
            return None

    @property
    @lru_cache()
    def _scheme(self) -> Scheme | None:
        try:
            return Scheme.objects.prefetch_related(
                "buildings", "buildings__rooms", "buildings__rooms__server_racks"
            ).get(id=self.cleaned_data['scheme_id'])
        except Scheme.DoesNotExist:
            return None

    @property
    def _access(self) -> Access | None:
        try:
            return (Access.objects.filter(
                Q(
                    object_type=self.scheme_content_type,
                    object_id=self._scheme.id,
                ),
                Q(
                    object_type=self.building_content_type,
                    object_id__in=self._scheme.buildings.values("id")
                ),
                Q(
                    object_type=self.room_content_type,
                    object_id=self._scheme.buildings.rooms.values("id"),
                ),
                Q(
                    object_type=self.server_rack_content_type,
                    object_id=self._scheme.buildings.rooms.server_racks.values("id"),
                ),
            ).filter(
                user=self.cleaned_data['current_user'],
                role__in=['Change', 'Creator'],
            ))
        except Access.DoesNotExist:
            return None

    def equipment_template_presence(self) -> None:
        if not self._equipment_template:
            self.add_error('equipment_template_id', ObjectDoesNotExist('Equipment template id='
                                                                       f'{self.cleaned_data["equipment_template_id"]}'
                                                                       ' not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def scheme_presence(self) -> None:
        if not self._scheme:
            self.add_error('filter_scheme_id', ObjectDoesNotExist(
                f'Server rack id={self.cleaned_data["scheme_id"]} not found'))
            self.response_status = status.HTTP_404_NOT_FOUND

    def access_presence(self) -> None:
        if self._scheme:
            if not self._access and not self.cleaned_data['current_user'].is_superuser:
                self.add_error('current_user', PermissionDenied('Access to the schema id = '
                                                                f'{self._scheme.id} is not granted'))
                self.response_status = status.HTTP_403_FORBIDDEN

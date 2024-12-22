from django import forms
from utils.services import ServiceWithResult

from models_app.models import EquipmentTemplateType


class ListEquipmentTypeService(ServiceWithResult):
    search_filter = forms.CharField(required=False)
    filter_active = forms.CharField(required=False)

    def process(self):
        if self.is_valid():
            self.result = self._filter_equipment_template_types
        return self

    @property
    def _filter_equipment_template_types(self):
        equipment_template_types = self._equipment_template_types
        if self.cleaned_data.get('filter_active'):
            equipment_template_types = equipment_template_types.filter(is_active=self.cleaned_data.get('filter_active'))
        if self.cleaned_data['search_filter']:
            equipment_template_types = equipment_template_types.filter(
                name__icontains=self.cleaned_data['search_filter']
            )
        return equipment_template_types

    @property
    def _equipment_template_types(self):
        try:
            return EquipmentTemplateType.objects.all()
        except EquipmentTemplateType.DoesNotExist:
            return EquipmentTemplateType.objects.none()

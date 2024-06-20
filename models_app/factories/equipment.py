from factory.django import DjangoModelFactory
import factory

from models_app.models.equipment import Equipment
from models_app.models.equipment_template import EquipmentTemplate


class EquipmentFactory(DjangoModelFactory):
    class Meta:
        model = Equipment

    template = factory.Iterator(EquipmentTemplate.objects.all().values_list('id', flat=True))

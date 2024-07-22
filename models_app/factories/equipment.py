from factory.django import DjangoModelFactory
import factory

from models_app.models.equipment import Equipment
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.room import Room


class EquipmentFactory(DjangoModelFactory):
    class Meta:
        model = Equipment

    template = factory.Iterator(EquipmentTemplate.objects.all().values_list('id', flat=True))
    room = factory.Iterator(Room.objects.all().values_list('id', flat=True) or None)

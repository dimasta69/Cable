from factory.django import DjangoModelFactory
import factory

from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.manufacturer import Manufacturer


class EquipmentTemplateFactory(DjangoModelFactory):
    class Meta:
        model = EquipmentTemplate

    manufacturer = factory.Iterator(Manufacturer.objects.all().values_list('id', flat=True))
    model = factory.Faker('sentence', nb_words=1)
    number_of_units = factory.Faker('random_int')
    power = factory.Faker('random_int')
    type = factory.Faker('word')

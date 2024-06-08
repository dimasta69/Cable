import factory
from factory.django import DjangoModelFactory

from models_app.models.port_template import PortTemplate
from models_app.models.equipment_template import EquipmentTemplate


class PortTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PortTemplate

    name = factory.Faker('sentence', nb_words=3)
    equipment_tmp = factory.Iterator(EquipmentTemplate.objects.all().values_list('id', flat=True))
    count = factory.Faker('random_int')
    
import factory
from factory.django import DjangoModelFactory

from models_app.models.port_template import PortTemplate
from models_app.models.equipment_template import EquipmentTemplate
from models_app.models.type_port import TypePort


class PortTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PortTemplate

    name = factory.Faker('sentence', nb_words=3)
    equipment_tmp = factory.Iterator(EquipmentTemplate.objects.all().values_list('id', flat=True))
    count = factory.Faker('random_int')
    type_port = factory.Iterator(TypePort.objects.all().values_list('id', flat=True))
    speed = factory.LazyAttribute(lambda _: [1, 2, 3, 4, 5])
    modular = False

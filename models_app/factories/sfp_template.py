from factory.django import DjangoModelFactory
import factory

from models_app.models.sfp_template import SfpTemplate
from models_app.models.manufacturer import Manufacturer
from models_app.models.type_port import TypePort


class SfpTemplateFactory(DjangoModelFactory):
    class Meta:
        model = SfpTemplate

    manufacturer = factory.Faker(Manufacturer.objects.all().values_list('id', flat=True))
    name = factory.Faker('sentence', nb_words=2)
    type_port = factory.Faker(TypePort.objects.all().values_list('id', flat=True))
    speed = factory.LazyAttribute(lambda _: [1, 2, 3, 4, 5])
    line_type = factory.Iterator(['Одномодовый', 'Многомодовый', 'Медный провод', 'None'])

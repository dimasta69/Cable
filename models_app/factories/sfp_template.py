import factory
from factory.django import DjangoModelFactory

from models_app.models.sfp_template import SfpTemplate
from models_app.models.manufacturer import Manufacturer


class SfpTemplateFactory(DjangoModelFactory):
    class Meta:
        model = SfpTemplate

    name = factory.Faker('sentence', nb_words=3)
    manufacturer = factory.Iterator(Manufacturer.objects.all().values_list('id', flat=True))
    speed = factory.Faker('random_int')

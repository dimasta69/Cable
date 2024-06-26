from factory.django import DjangoModelFactory
import factory

from models_app.models.building import Building
from models_app.models.scheme import Scheme


class BuildingFactory(DjangoModelFactory):
    class Meta:
        model = Building

    scheme = factory.Iterator(Scheme.objects.all().values_list('id', flat=True))
    number = factory.Faker('sentence', nb_words=3)
    coord_x = factory.Faker('random_int')
    coord_y = factory.Faker('random_int')

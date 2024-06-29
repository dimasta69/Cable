from factory.django import DjangoModelFactory
import factory

from models_app.models.room import Room
from models_app.models.building import Building


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = Room

    building = factory.Iterator(Building.objects.all().values_list('id', flat=True))
    number = factory.Faker('sentence', nb_words=1)
    type = factory.Iterator(['Серверная', 'Обычная'])

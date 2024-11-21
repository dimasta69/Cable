from factory.django import DjangoModelFactory
import factory

from models_app.models.room import Room
from models_app.models.server_rack import ServerRack


class ServerRackFactory(DjangoModelFactory):
    class Meta:
        model = ServerRack

    room = factory.Iterator(Room.objects.all().values_list('id', flat=True))
    number_of_units = factory.Faker('random_int')
    title = factory.Faker('sentence', nb_words=1)
    max_power = factory.Faker('random_int')

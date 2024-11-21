from factory.django import DjangoModelFactory
import factory

from models_app.models.equipment import Equipment
from models_app.models.server_rack import ServerRack
from models_app.models.unit import Unit


class UnitFactory(DjangoModelFactory):
    class Meta:
        model = Unit

    uid = factory.Faker('random_int')
    server_rack = factory.Iterator(Equipment.objects.all().values_list('id', flat=True))
    equipment = factory.Iterator(ServerRack.objects.all().values_list('id', flat=True) or None)
    side = factory.Iterator(['Лицевая', 'Тыльная'])

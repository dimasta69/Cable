from factory.django import DjangoModelFactory
import factory

from models_app.models.port import Port
from models_app.models.equipment import Equipment


class PortFactory(DjangoModelFactory):
    class Meta:
        model = Port

    uid = factory.Faker('random_int')
    equipment = factory.Iterator(Equipment.objects.all().values_list('id', flat=True))
    line_type = factory.Iterator(['Одномодовый', 'Многомодовый', 'Медный провод', 'None'])
    vlan_type = factory.Iterator(['Access', 'Trunk', 'None'])
    ip = factory.Faker('ipv4')
    mac = factory.Faker('mac_address')
    connection = factory.Iterator(Equipment.objects.all().values_list('id', flat=True) or None)

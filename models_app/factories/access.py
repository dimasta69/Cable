import factory
from factory.django import DjangoModelFactory

from models_app.models.access import Access
from models_app.models.user import User
from models_app.models.scheme import Scheme


class AccessFactory(DjangoModelFactory):
    class Meta:
        model = Access

    user = factory.Iterator(User.objects.all().values_list('id', flat=True))
    scheme = factory.Iterator(Scheme.objects.all().values_list('id', flat=True))
    role = factory.Iterator(['Read', 'Change', 'Creator'])

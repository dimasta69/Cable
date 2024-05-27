import factory
from factory.django import DjangoModelFactory

from models_app.models.scheme import Scheme
from models_app.models.user import User


class SchemeFactory(DjangoModelFactory):
    class Meta:
        model = Scheme

    title = factory.Faker('sentence', nb_words=3)
    creator = factory.Iterator(User.objects.all().values_list('id', flat=True))

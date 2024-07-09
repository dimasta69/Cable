from factory.django import DjangoModelFactory
import factory

from models_app.models.type_port import TypePort


class TypePortFactory(DjangoModelFactory):
    class Meta:
        model = TypePort

    name = factory.Faker('sentence', nb_words=1)

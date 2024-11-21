from factory.django import DjangoModelFactory
import factory

from models_app.models.manufacturer import Manufacturer


class ManufacturerFactory(DjangoModelFactory):
    class Meta:
        model = Manufacturer

    name = factory.Faker('sentence', nb_words=3)

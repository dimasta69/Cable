import factory
from factory.django import DjangoModelFactory

from models_app.models.port_template import PortTemplate


class PortTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PortTemplate

    name = factory.Faker('sentence', nb_words=3)
    
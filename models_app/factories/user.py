import factory
from factory.django import DjangoModelFactory

from models_app.models.user import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")

    @factory.post_generation
    def set_password(self, created, extracted, **kwargs):
        self.set_password('Dima2012')


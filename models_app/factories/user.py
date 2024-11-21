import factory
from factory.django import DjangoModelFactory

from models_app.models.user import User
from rest_framework.authtoken.models import Token


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall('set_password', 'password')

    @factory.post_generation
    def create_token(self, create, extracted, **kwargs):
        if create:
            self.save()
            Token.objects.create(user=self)

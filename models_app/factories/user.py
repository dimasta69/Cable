from factory.django import DjangoModelFactory
import factory
from rest_framework_simplejwt.tokens import RefreshToken

from models_app.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('sentence', nb_words=1)
    password = factory.Faker('sentence', nb_words=1)

    @factory.post_generation
    def set_token(obj, create, extracted, **kwargs):
        if create:
            refresh = RefreshToken.for_user(obj)
            access_token = str(refresh.access_token)
            obj.access_token = access_token
            obj.save()

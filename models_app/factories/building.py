from factory.django import DjangoModelFactory
import factory
from django.contrib.contenttypes.models import ContentType

from models_app.models import Building, Scheme, Access
from models_app.factories.user import UserFactory


class SchemeFactory(DjangoModelFactory):
    class Meta:
        model = Scheme

    title = factory.Faker('sentence', nb_words=3)
    creator = factory.SubFactory(UserFactory)


class AccessFactory(DjangoModelFactory):
    class Meta:
        model = Access


class BuildingFactory(DjangoModelFactory):
    class Meta:
        model = Building

    scheme = factory.SubFactory(SchemeFactory)
    name = factory.Faker('sentence', nb_words=3)
    coord_x = factory.Faker('random_int')
    coord_y = factory.Faker('random_int')

    @factory.post_generation
    def create_access(obj, create, extracted, **kwargs):
        if create:
            AccessFactory.create(
                role='Creator',
                object_id=obj.id,
                object_type=ContentType.objects.get_for_model(Building),
                user=obj.scheme.creator,
            )

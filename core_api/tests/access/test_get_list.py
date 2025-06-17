import json

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from models_app.factories.building import AccessFactory, BuildingFactory
from models_app.models import Scheme


class AccessTestList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building_1 = BuildingFactory()
        cls.building_2 = BuildingFactory()
        AccessFactory.create(
            role='Creator',
            object_id=cls.building_1.scheme.id,
            object_type=ContentType.objects.get_for_model(Scheme),
            user=cls.building_1.scheme.creator,
        )
        AccessFactory.create(
            role='Creator',
            object_id=cls.building_2.scheme.id,
            object_type=ContentType.objects.get_for_model(Scheme),
            user=cls.building_2.scheme.creator,
        )

    def test_access_granted_return_403(self):
        query_params = {
            'filter_scheme_id': self.building_1.scheme.id,
        }
        resp = self.client.get(
            '/core_api/access/',
            query_params=query_params,
            HTTP_AUTHORIZATION=f'Token {self.building_2.scheme.creator.access_token}'
        )
        self.assertEqual(resp.status_code, 403)

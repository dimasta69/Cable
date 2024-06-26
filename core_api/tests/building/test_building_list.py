import json
from django.test import TestCase
from django.test.client import Client, encode_multipart

from models_app.factories.scheme import SchemeFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.user import UserFactory


class BuildingListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_3 = SchemeFactory.create(creator=cls.user_1)
        cls.building_list_1 = BuildingFactory.create_batch(20, scheme=cls.scheme_1)
        cls.building_list_2 = BuildingFactory.create_batch(2, scheme=cls.scheme_2)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_3)

    def test_return_200(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/building/', {'filter_scheme_id': self.scheme_1.id})
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json) == 20)

    def test_return_404_not_found_scheme(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/building/', {'filter_scheme_id': 99})
        self.assertEqual(resp.status_code, 404)

    def test_return_201_create(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        content = encode_multipart('BoUnDaRyStRiNg', {
            'scheme_id': self.scheme_1.id,
            'number': 'test',
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.post(f'/core_api/building/',
                                content,
                                content_type=content_type)
        self.assertEqual(resp.status_code, 201)

    def test_return_404_create_scheme_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        content = encode_multipart('BoUnDaRyStRiNg', {
            'scheme_id': 99,
            'number': 'test',
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.post(f'/core_api/building/',
                                content,
                                content_type=content_type)
        self.assertEqual(resp.status_code, 404)

    def test_return_422_create_scheme_number_repeat(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        content = encode_multipart('BoUnDaRyStRiNg', {
            'scheme_id': self.scheme_3.id,
            'number': self.building_1.number.lower(),
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.post(f'/core_api/building/',
                                content,
                                content_type=content_type)
        self.assertEqual(resp.status_code, 422)

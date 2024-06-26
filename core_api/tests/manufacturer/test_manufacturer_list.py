import json
from django.test import TestCase
from django.test.client import Client

from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class ManufacturerListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)
        cls.manufacturer = ManufacturerFactory.create_batch(20)
        cls.manufacturer_1 = ManufacturerFactory.create()

        cls.client = Client()

    def test_return_200_min_params(self):
        resp = self.client.get('/core_api/manufacturer/', content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 21)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

    def test_return_200_max_params(self):
        data = {'order_by': '-name', 'page': 2, 'per_page': 5}
        resp = self.client.get('/core_api/manufacturer/',
                               data,
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == 5)
        self.assertTrue(len(resp_json['results']) == 5)

    def test_search_200(self):
        data = {'search_filter': self.manufacturer_1.name}
        resp = self.client.get('/core_api/manufacturer/', data,
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_create_return_200(self):
        data = {'name': 'test'}
        resp = self.client.post('/core_api/manufacturer/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_create_return_422_warning_title(self):
        data = {'name': 'test'}
        resp = self.client.post('/core_api/manufacturer/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 201)
        data = {'name': 'test'}
        resp = self.client.post('/core_api/manufacturer/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

import json
from django.test import TestCase

from models_app.factories.type_port import TypePortFactory
from models_app.factories.sfp_template import SfpTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class SfpTemplateListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()

        cls.type_port_1 = TypePortFactory.create()
        cls.type_port_2 = TypePortFactory.create()

        cls.sfp_template_list_1 = SfpTemplateFactory.create_batch(14, manufacturer=cls.manufacturer_1,
                                                                  type_port=cls.type_port_1, line_type='Многомодовый')
        cls.sfp_template_list_2 = SfpTemplateFactory.create_batch(6, manufacturer=cls.manufacturer_2,
                                                                  type_port=cls.type_port_2, line_type='Одномодовый',
                                                                  speed=[10, 100])
        cls.sfp_template_1 = SfpTemplateFactory.create(manufacturer=cls.manufacturer_2, type_port=cls.type_port_1,
                                                       line_type='Многомодовый', )

    def test_return_200_min_params(self):
        resp = self.client.get('/core_api/sfp_template/', content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 21)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

    def test_return_401_not_auth(self):
        resp = self.client.get('/core_api/sfp_template/', content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_return_200_filter_manufacturer(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_manufacturer_id': self.manufacturer_1.id},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['total_count'] == 14)

    def test_return_404_not_found_manufacturer(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_manufacturer_id': 99},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_filter_type_port(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_type_port_id': self.type_port_2.id},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['total_count'] == 6)

    def test_return_404_type_port_not_found(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_type_port_id': 99},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_filter_speed(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_speed': 100},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['total_count'] == 6)

    def test_200_search_filter(self):
        resp = self.client.get('/core_api/sfp_template/', {'search_filter': self.sfp_template_1.name},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['total_count'] == 1)

    def test_return_200_filter_line_type(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_line_type': "Одномодовый"},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['total_count'] == 6)

    def test_return_404_line_type_not_found(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_line_type': "fdsf"},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_max_params(self):
        resp = self.client.get('/core_api/sfp_template/', {'filter_line_type': "Многомодовый",
                                                           'filter_manufacturer_id': self.manufacturer_2.id,
                                                           'filter_type_port_id': self.type_port_1.id,
                                                           'filter_speed': 1,
                                                           'search_filter': self.sfp_template_1.name},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['total_count'] == 1)

    def test_201_create_sfp(self):
        resp = self.client.post('/core_api/sfp_template/',
                                {'manufacturer_id': self.manufacturer_1.id, 'name': 'test123',
                                 'type_port_id': self.type_port_1.id,
                                 'line_type': 'Многомодовый', 'speed': [1, 10, 100]},
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp_json['manufacturer'] == self.manufacturer_1.name)
        self.assertTrue(resp_json['name'] == "test123")
        self.assertTrue(resp_json['type_port'] == self.type_port_1.name)
        self.assertTrue(resp_json['speed'] == [1, 10, 100])
        self.assertTrue(resp_json['line_type'] == "Многомодовый")

    def test_return_404_create_manufacturer_not_found(self):
        resp = self.client.post('/core_api/sfp_template/',
                                {'manufacturer_id': 99, 'name': 'test123',
                                 'type_port_id': self.type_port_1.id,
                                 'line_type': 'Многомодовый', 'speed': [1, 10, 100]},
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_create_type_port_not_found(self):
        resp = self.client.post('/core_api/sfp_template/',
                                {'manufacturer_id': self.manufacturer_1.id, 'name': 'test123',
                                 'type_port_id': 99,
                                 'line_type': 'Многомодовый', 'speed': [1, 10, 100]},
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_create_line_type_not_found(self):
        resp = self.client.post('/core_api/sfp_template/',
                                {'manufacturer_id': self.manufacturer_1.id, 'name': 'test123',
                                 'type_port_id': 99,
                                 'line_type': 'test', 'speed': [1, 10, 100]},
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

import json
from django.test import TestCase
from django.test.client import Client

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class EquipmentTemplateListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()
        cls.equipment_template = EquipmentTemplateFactory.create_batch(20, manufacturer=cls.manufacturer_1)
        cls.equipment_template_2 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_2)

        cls.port_template = PortTemplateFactory.create_batch(18, equipment_tmp=cls.equipment_template_2, count=3)

    def test_return_200_min_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment_template/', content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 21)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

    def test_return_200_max_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'order_by': '-model', 'page': 2, 'per_page': 5}
        resp = self.client.get('/core_api/equipment_template/',
                               data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == 5)
        self.assertTrue(len(resp_json['results']) == 5)

    def test_search_200(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'search_filter': self.manufacturer_2.name}
        resp = self.client.get('/core_api/equipment_template/', data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_create_return_200(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'type': 'Сервер', 'model': 'test', 'number_of_units': 3, 'power': 250,
                'manufacturer_id': self.manufacturer_1.id}
        resp = self.client.post('/core_api/equipment_template/', data)
        self.assertEqual(resp.status_code, 201)

    def test_create_return_422_warning_model(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'type': ' Сервер', 'model': 'test', 'number_of_units': 3, 'power': 250,
                'manufacturer_id': self.manufacturer_1.id}
        resp = self.client.post('/core_api/equipment_template/', data)
        self.assertEqual(resp.status_code, 201)
        data = {'type': ' Сервер', 'model': 'test', 'number_of_units': 3, 'power': 250,
                'manufacturer_id': self.manufacturer_1.id}
        resp = self.client.post('/core_api/equipment_template/', data)
        self.assertEqual(resp.status_code, 422)

    def test_return_200_filter_manufacturer(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment_template/', {'filter_manufacturer': self.manufacturer_2.id},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.content)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_return_404_manufacturer_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'type': ' Сервер', 'model': 'test', 'number_of_units': 3, 'power': 250,
                'manufacturer_id': 99}
        resp = self.client.post('/core_api/equipment_template/', data)
        self.assertEqual(resp.status_code, 404)

    def test_return_404_type_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'type': ' 123', 'model': 'test', 'number_of_units': 3, 'power': 250,
                'manufacturer_id': self.manufacturer_1.id}
        resp = self.client.post('/core_api/equipment_template/', data)
        self.assertEqual(resp.status_code, 404)

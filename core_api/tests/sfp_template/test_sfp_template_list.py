import json
from django.test import TestCase
from django.test.client import Client

from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.sfp_template import SfpTemplateFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class SfpTemplateListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()

        cls.sfp_template = SfpTemplateFactory.create_batch(20, manufacturer=cls.manufacturer_1)
        cls.sfp_template_1 = SfpTemplateFactory.create(manufacturer=cls.manufacturer_2)

        cls.client = Client()

    def test_return_200_min_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/sfp_template/', content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 21)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

    def test_return_200_max_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'order_by': '-name', 'page': 2, 'per_page': 5}
        resp = self.client.get('/core_api/sfp_template/',
                               data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == 5)
        self.assertTrue(len(resp_json['results']) == 5)

    def test_return_200_filter_manufacturer(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'filter_manufacturer': self.manufacturer_2.id}
        resp = self.client.get('/core_api/sfp_template/',
                               data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_return_404_filter_manufacturer_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'filter_manufacturer': 99}
        resp = self.client.get('/core_api/sfp_template/',
                               data,
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_search_filter(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'search_filter': self.manufacturer_2.name}
        resp = self.client.get('/core_api/sfp_template/',
                               data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

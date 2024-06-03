import json
from django.test import TestCase
from django.test.client import Client

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class PortTemplateListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()

        cls.port_template = PortTemplateFactory.create_batch(20)
        cls.port_template1 = PortTemplateFactory.create()

    def test_return_200_min_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/port_template/', content_type='application/json')
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
        resp = self.client.get('/core_api/port_template/',
                               data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == 5)
        self.assertTrue(len(resp_json['results']) == 5)

    def test_search_200(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'search_filter': self.port_template1.name}
        resp = self.client.get('/core_api/port_template/', data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_create_return_200(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'name': 'test'}
        resp = self.client.post('/core_api/port_template/', data)
        self.assertEqual(resp.status_code, 201)

    def test_create_return_422_warning_title(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'name': 'test'}
        resp = self.client.post('/core_api/port_template/', data)
        self.assertEqual(resp.status_code, 201)
        data = {'name': 'test'}
        resp = self.client.post('/core_api/port_template/', data)
        self.assertEqual(resp.status_code, 422)

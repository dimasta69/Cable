from django.test import TestCase
from django.test.client import Client, encode_multipart
import json

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory


class PortTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()

        cls.port_template = PortTemplateFactory.create_batch(20)
        cls.port_template1 = PortTemplateFactory.create()

    def test_return_200_valid_login(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.get(f'/core_api/port_template/{self.port_template1.id}/',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_return_200_no_login(self):
        resp = self.client.get(f'/core_api/port_template/{self.port_template1.id}/',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_return_200_change_name(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'name': 'test_1'})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type)
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['name'] == 'test_1')

    def test_return_422_change_valid_name(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'name': self.port_template1.name})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type)
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_found(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp_get = self.client.get('/core_api/port_template/55/')
        content = encode_multipart('BoUnDaRyStRiNg', {'name': 'test_1'})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp_update = self.client.put('/core_api/port_template/55/',
                                      content, content_type=content_type)
        resp_delete = self.client.delete('/core_api/port_template/55/')
        self.assertEqual(resp_get.status_code, 404)
        self.assertEqual(resp_update.status_code, 404)
        self.assertEqual(resp_delete.status_code, 404)


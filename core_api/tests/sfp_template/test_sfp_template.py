import json
from django.test import TestCase
from django.test.client import Client, encode_multipart

from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.sfp_template import SfpTemplateFactory


class SfpTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()

        cls.sfp_template = SfpTemplateFactory.create_batch(20, manufacturer=cls.manufacturer_1)
        cls.sfp_template_1 = SfpTemplateFactory.create(manufacturer=cls.manufacturer_2)
        cls.sfp_template_2 = SfpTemplateFactory.create(manufacturer=cls.manufacturer_2)

        cls.client = Client()

    def test_return_200(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get(f'/core_api/sfp_template/{self.sfp_template_1.id}/', content_type=
        'application/json')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/sfp_template/99/', content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_change_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        content = encode_multipart('BoUnDaRyStRiNg', {'name': 'name', 'speed': 1000})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/', content,
                               content_type=content_type)
        resp_json = json.loads(resp.content)
        print(resp_json)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['speed'] == 1000)
        self.assertTrue(resp_json['name'] == 'name')

    def test_return_422_name_repeat(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        content = encode_multipart('BoUnDaRyStRiNg', {'name': self.sfp_template_1.name, 'speed': 1000})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_2.id}/', content,
                               content_type=content_type)
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_found_sfp_template(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        content = encode_multipart('BoUnDaRyStRiNg', {'name': self.sfp_template_1.name, 'speed': 1000})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/sfp_template/99/', content,
                               content_type=content_type)
        self.assertEqual(resp.status_code, 404)

    def test_return_204_delete_sfp_template(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.delete(f'/core_api/sfp_template/{self.sfp_template_1.id}/', content_type=
        'application/json')
        self.assertEqual(resp.status_code, 204)

    def test_return_404_delete_sfp_template_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.delete('/core_api/sfp_template/99/', content_type=
        'application/json')
        self.assertEqual(resp.status_code, 404)

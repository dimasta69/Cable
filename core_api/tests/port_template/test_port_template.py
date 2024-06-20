from django.test import TestCase
from django.test.client import Client, encode_multipart
import json

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory


class PortTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()
        cls.manufacturer = ManufacturerFactory.create()
        cls.equipment_template = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer)
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer)
        cls.port_template1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template)

    def test_return_200_valid_login(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.get(f'/core_api/port_template/{self.port_template1.id}/',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_return_401_no_login(self):
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
        self.assertEqual(resp.status_code, 422)

    def test_return_200_update_count(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'count': 3})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type)
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['count'] == 3)

    def test_return_200_update_equipment_template(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'equipment_tmp_id': self.equipment_template_1.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type)
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['equipment_tmp']['model'] == self.equipment_template_1.model)

    def test_return_404_not_found_equipment_template(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'equipment_tmp_id': 99})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 404)

    def test_return_200_change_speed(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'speed': [1, 20]})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.content)
        self.assertTrue(resp_json['speed'] == [1, 20])

    def test_return_200_update_max_params(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'equipment_tmp_id': self.equipment_template_1.id,
                                                      'name': 'test_10', 'count': 10, 'speed': ['10', '100']})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type)
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['equipment_tmp']['model'] == self.equipment_template_1.model)

    def test_return_404_not_found(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp_get = self.client.get('/core_api/port_template/99/')
        content = encode_multipart('BoUnDaRyStRiNg', {'name': 'test_1'})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp_update = self.client.put('/core_api/port_template/99/',
                                      content, content_type=content_type)
        resp_delete = self.client.delete('/core_api/port_template/99/')
        self.assertEqual(resp_get.status_code, 404)
        self.assertEqual(resp_update.status_code, 404)
        self.assertEqual(resp_delete.status_code, 404)

    def test_return_204_delete(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.delete(f'/core_api/port_template/{self.port_template1.id}/')
        self.assertTrue(resp.status_code, 204)

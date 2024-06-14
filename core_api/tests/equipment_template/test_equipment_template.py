import json
from django.test import TestCase
from django.test.client import Client, encode_multipart

from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.port_template import PortTemplateFactory


class EquipmentTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1)
        cls.equipment_template_2 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_2)

        cls.port_template = PortTemplateFactory.create_batch(3, equipment_tmp=cls.equipment_template_2, count=3)

    def test_return_200_get(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get(f'/core_api/equipment_template/{self.equipment_template_1.id}/')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_id_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp_get = self.client.get('/core_api/equipment_template/99/')
        resp_put = self.client.get('/core_api/equipment_template/99/')
        resp_delete = self.client.get('/core_api/equipment_template/99/')
        self.assertEqual(resp_get.status_code, 404)
        self.assertEqual(resp_put.status_code, 404)
        self.assertEqual(resp_delete.status_code, 404)

    def test_return_200_update_max_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")

        content = encode_multipart('BoUnDaRyStRiNg', {
            'manufacturer_id': self.manufacturer_2.id,
            'type': 'Коммутатор',
            'model': 'test_1',
            'number_of_units': 1,
            'power': 1,
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment_template/{self.equipment_template_1.id}/',
                               content, content_type=content_type)
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['manufacturer']['name'] == self.manufacturer_2.name)
        self.assertTrue(resp_json['type'] == 'Коммутатор')
        self.assertTrue(resp_json['model'] == 'test_1')
        self.assertTrue(resp_json['number_of_units'] == 1)
        self.assertTrue(resp_json['power'] == 1)

    def test_return_404_update_manufacturer_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")

        content = encode_multipart('BoUnDaRyStRiNg', {
            'manufacturer_id': 99,
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment_template/{self.equipment_template_1.id}/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 404)

    def test_return_404_update_type_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")

        content = encode_multipart('BoUnDaRyStRiNg', {
            'type': '123',
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment_template/{self.equipment_template_1.id}/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 404)

    def test_return_422_model_presence(self):
        self.client.login(username=self.user_1.username, password="Dima2012")

        content = encode_multipart('BoUnDaRyStRiNg', {
            'model': 'title',
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment_template/{self.equipment_template_1.id}/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 200)

        content = encode_multipart('BoUnDaRyStRiNg', {
            'model': 'title',
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment_template/{self.equipment_template_2.id}/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 422)

    def test_return_204_delete(self):
        self.client.login(username=self.user_1.username, password="Dima2012")

        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.delete(f'/core_api/equipment_template/{self.equipment_template_1.id}/',
                                  content_type=content_type)
        self.assertEqual(resp.status_code, 204)

    def test_return_count_ports(self):
        self.client.login(username=self.user_1.username, password="Dima2012")

        resp = self.client.get(f'/core_api/equipment_template/{self.equipment_template_2.id}/')
        resp_json = json.loads(resp.content)
        self.assertTrue(resp_json['count_port'] == 9)

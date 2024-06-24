import json
from django.test import TestCase
from django.test.client import Client

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.equipment import EquipmentFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class EquipmentListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()
        cls.manufacturer_3 = ManufacturerFactory.create()
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1)
        cls.equipment_template_2 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_2, type='Сервер')
        cls.equipment_template_3 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1)
        cls.equipment_template_4 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_3)

        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=20)
        cls.port_template_2 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=4)

        cls.port_template_3 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_2, count=18)
        cls.port_template_4 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_2, count=2)

        cls.port_template_5 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_4, count=14)

        cls.equipment = EquipmentFactory.create_batch(17, template=cls.equipment_template_1)
        cls.equipment_2 = EquipmentFactory.create_batch(2, template=cls.equipment_template_2)
        cls.equipment_3 = EquipmentFactory.create(template=cls.equipment_template_4)

    def test_return_200_min_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment/', content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 20)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

    def test_return_200_max_params(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        data = {'order_by': '-template__model', 'page': 2, 'per_page': 5}
        resp = self.client.get('/core_api/equipment/',
                               data,
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == 5)
        self.assertTrue(len(resp_json['results']) == 5)

    def test_return_201_create_equipment(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.post('/core_api/equipment/', {'equipment_template_id': self.equipment_template_1.
                                id, 'vlan_ip': '{"2": "10.16.7.110"}'})
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp_json['free_ports'] == 24)

    def test_return_404_create_equipment_template_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.post('/core_api/equipment/', {'equipment_template_id': 99})
        self.assertEqual(resp.status_code, 404)

    def test_return_404_create_port_template_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.post('/core_api/equipment/', {'equipment_template_id': self.equipment_template_3.
                                id})
        self.assertEqual(resp.status_code, 404)

    def test_return_200_filter_manufacturer(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment/', {'filter_manufacturer': self.equipment_template_2.
                               manufacturer.id}, content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 2)

    def test_return_404_filter_valid_manufacturer(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment/', {'filter_manufacturer': 99},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_filter_type(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment/', {'filter_type': self.equipment_template_2.type},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_filter_valid_type(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment/', {'filter_type': 'fdsf'},
                               content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_search_filter(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment/', {'search_filter': self.equipment_template_4.model},
                               content_type='application/json')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

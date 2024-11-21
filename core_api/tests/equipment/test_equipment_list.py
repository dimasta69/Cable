import json
from django.test import TestCase

from models_app.factories.building import BuildingFactory
from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.room import RoomFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.server_rack import ServerRackFactory
from models_app.factories.type_port import TypePortFactory
from models_app.factories.unit import UnitFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.equipment import EquipmentFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class EquipmentListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()
        cls.manufacturer_3 = ManufacturerFactory.create()
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1, number_of_units=2,
                                                                   power=150)
        cls.equipment_template_2 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_2, type='Сервер')
        cls.equipment_template_3 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1, number_of_units=2)
        cls.equipment_template_4 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_3)

        cls.type_port_1 = TypePortFactory.create()

        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=20,
                                                         type_port=cls.type_port_1)
        cls.port_template_2 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=4,
                                                         type_port=cls.type_port_1)

        cls.port_template_3 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_2, count=18,
                                                         type_port=cls.type_port_1)
        cls.port_template_4 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_2, count=2,
                                                         type_port=cls.type_port_1)

        cls.port_template_5 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_4, count=14,
                                                         type_port=cls.type_port_1)

        cls.equipment = EquipmentFactory.create_batch(17, template=cls.equipment_template_1, room=None)
        cls.equipment_2 = EquipmentFactory.create_batch(2, template=cls.equipment_template_2, room=None)
        cls.equipment_3 = EquipmentFactory.create(template=cls.equipment_template_4, room=None)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)

        cls.room_1 = RoomFactory.create(building=cls.building_1, type='Серверная')
        cls.room_2 = RoomFactory.create(building=cls.building_1, type='Серверная')

        cls.server_rack_1 = ServerRackFactory.create(room=cls.room_1, number_of_units=20, max_power=None)
        cls.server_rack_2 = ServerRackFactory.create(room=cls.room_1, number_of_units=20)
        cls.server_rack_3 = ServerRackFactory.create(room=cls.room_1, number_of_units=20, max_power=100)
        cls.server_rack_4 = ServerRackFactory.create(room=cls.room_1, number_of_units=20, max_power=200)

        cls.unit_1 = UnitFactory.create(server_rack=cls.server_rack_1, side='Лицевая', equipment=None)
        cls.unit_2 = UnitFactory.create(server_rack=cls.server_rack_1, side='Лицевая', equipment=None)
        cls.unit_3 = UnitFactory.create(server_rack=cls.server_rack_1, side='Лицевая', equipment=None)
        cls.unit_4 = UnitFactory.create(server_rack=cls.server_rack_2, side='Лицевая', equipment=None)
        cls.unit_5 = UnitFactory.create(server_rack=cls.server_rack_3, side='Лицевая', equipment=None)
        cls.unit_6 = UnitFactory.create(server_rack=cls.server_rack_3, side='Лицевая', equipment=None)
        cls.unit_7 = UnitFactory.create(server_rack=cls.server_rack_4, side='Лицевая', equipment=None)
        cls.unit_8 = UnitFactory.create(server_rack=cls.server_rack_4, side='Лицевая', equipment=None)

    def test_return_200_min_params(self):
        resp = self.client.get('/core_api/equipment/', content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 20)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

    def test_return_200_max_params(self):
        data = {'order_by': '-template__model', 'page': 2, 'per_page': 5}
        resp = self.client.get('/core_api/equipment/',
                               data,
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == 5)
        self.assertTrue(len(resp_json['results']) == 5)

    def test_return_201_create_equipment(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_1.id, self.unit_2.id],
            'server_rack_id': self.server_rack_1.id,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 201)

    def test_return_404_create_equipment_template_not_found(self):
        resp = self.client.post('/core_api/equipment/', {'equipment_template_id': 99,
                                                         'unit_list_id': [self.unit_1.id, self.unit_2.id],
                                                         'server_rack_id': self.server_rack_1.id,
                                                         },
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_create_port_template_not_found(self):
        resp = self.client.post('/core_api/equipment/', {'equipment_template_id': self.equipment_template_3.id,
                                                         'unit_list_id': [self.unit_1.id, self.unit_2.id],
                                                         'server_rack_id': self.server_rack_1.id, },
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_filter_manufacturer(self):
        resp = self.client.get('/core_api/equipment/', {'filter_manufacturer': self.equipment_template_2.
                               manufacturer.id}, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 2)

    def test_return_404_filter_valid_manufacturer(self):
        resp = self.client.get('/core_api/equipment/', {'filter_manufacturer': 99},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_filter_type(self):
        resp = self.client.get('/core_api/equipment/', {'filter_type': self.equipment_template_2.type},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_filter_valid_type(self):
        resp = self.client.get('/core_api/equipment/', {'filter_type': 'fdsf'},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_search_filter(self):
        resp = self.client.get('/core_api/equipment/', {'search_filter': self.equipment_template_4.model},
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_return_422_units_more_number_of_units(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_1.id, self.unit_2.id, self.unit_3.id],
            'server_rack_id': self.server_rack_1.id,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 422)

    def test_return_422_units_less_number_of_units(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_1.id],
            'server_rack_id': self.server_rack_1.id,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_valid_unit(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_1.id, 99],
            'server_rack_id': self.server_rack_1.id,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_server_rack_not_found(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_1.id, self.unit_2.id],
            'server_rack_id': 99,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_422_unit_correspond(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_1.id, self.unit_4.id],
            'server_rack_id': self.server_rack_1.id,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 422)

    def test_return_422_max_power(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_5.id, self.unit_6.id],
            'server_rack_id': self.server_rack_3.id,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 422)

    def test_return_201_max_power(self):
        content = {
            'equipment_template_id': self.equipment_template_1.id,
            'vlan_ip': '{"2": "10.16.7.110"}',
            'unit_list_id': [self.unit_7.id, self.unit_8.id],
            'server_rack_id': self.server_rack_4.id,
        }
        resp = self.client.post('/core_api/equipment/', content, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                content_type='application/json')
        self.assertEqual(resp.status_code, 201)

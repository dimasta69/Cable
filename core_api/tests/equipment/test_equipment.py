import json

from django.test import TestCase
from django.test.client import encode_multipart

from models_app.factories.building import BuildingFactory
from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.room import RoomFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.server_rack import ServerRackFactory
from models_app.factories.unit import UnitFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.equipment import EquipmentFactory
from models_app.factories.type_port import TypePortFactory


class EquipmentListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()
        cls.manufacturer_3 = ManufacturerFactory.create()
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1)
        cls.equipment_template_2 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_2, type='Сервер')
        cls.equipment_template_3 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1, number_of_units=3,
                                                                   power=None)
        cls.equipment_template_4 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_3)

        cls.type_port_1 = TypePortFactory.create()

        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=20,
                                                         modular=False, type_port=cls.type_port_1)
        cls.port_template_2 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=4,
                                                         modular=False, type_port=cls.type_port_1)

        cls.port_template_3 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_2, count=18,
                                                         modular=False, type_port=cls.type_port_1)
        cls.port_template_4 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_2, count=2,
                                                         modular=False, type_port=cls.type_port_1)

        cls.port_template_5 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_4, count=14,
                                                         modular=False, type_port=cls.type_port_1)

        cls.equipment = EquipmentFactory.create_batch(17, template=cls.equipment_template_1)
        cls.equipment_2 = EquipmentFactory.create(template=cls.equipment_template_3)
        cls.equipment_3 = EquipmentFactory.create(template=cls.equipment_template_4)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)
        cls.building_2 = BuildingFactory.create(scheme=cls.scheme_2)

        cls.room_1 = RoomFactory.create(building=cls.building_1, type='Серверная')
        cls.room_2 = RoomFactory.create(building=cls.building_1, type='Серверная')

        cls.server_rack_1 = ServerRackFactory.create(room=cls.room_1, number_of_units=20)

        cls.unit_1 = UnitFactory.create(server_rack=cls.server_rack_1, side='Лицевая', equipment=None)
        cls.unit_2 = UnitFactory.create(server_rack=cls.server_rack_1, side='Лицевая', equipment=None)
        cls.unit_3 = UnitFactory.create(server_rack=cls.server_rack_1, side='Лицевая', equipment=None)

    def test_return_200_get_equipment(self):
        resp = self.client.get(f'/core_api/equipment/{self.equipment_3.id}/',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_not_found(self):
        resp = self.client.get('/core_api/equipment/99/', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_204_delete(self):
        resp = self.client.delete(f'/core_api/equipment/{self.equipment_3.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 204)

    def test_return_404_delete(self):
        resp = self.client.delete('/core_api/equipment/99/', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_update_change(self):
        content = {
            'vlan_ip': '{"2": "10.16.7.150"}',
        }
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/equipment/{self.equipment_3.id}/',
                               content,
                               content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_update_not_found(self):
        content = {
            'vlan_ip': '{"2": "10.16.7.150"}',
        }
        content_type = 'application/json'
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.put('/core_api/equipment/99/', content, content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_add_equipment_for_unit(self):
        content = encode_multipart('BoUnDaRyStRiNg', {
            'unit_list_id': [self.unit_1.id, self.unit_2.id, self.unit_3.id],
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment/{self.equipment_2.id}/add_equipment_for_unit/',
                               content,
                               content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_add_equipment_list_id_not_found(self):
        content = encode_multipart('BoUnDaRyStRiNg', {
            'unit_list_id': [self.unit_1.id, self.unit_2.id, 99],
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment/{self.equipment_2.id}/add_equipment_for_unit/',
                               content,
                               content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_add_equipment_not_found(self):
        content = encode_multipart('BoUnDaRyStRiNg', {
            'unit_list_id': [self.unit_1.id, self.unit_2.id, self.unit_3.id],
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put('/core_api/equipment/99/add_equipment_for_unit/',
                               content,
                               content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_422_an_insufficient_amount_units(self):
        content = encode_multipart('BoUnDaRyStRiNg', {
            'unit_list_id': [self.unit_1.id, self.unit_2.id],
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment/{self.equipment_2.id}/add_equipment_for_unit/',
                               content,
                               content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_422_large_quantity_units(self):
        content = encode_multipart('BoUnDaRyStRiNg', {
            'unit_list_id': [self.unit_1.id, self.unit_2.id],
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment/{self.equipment_2.id}/add_equipment_for_unit/',
                               content,
                               content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_401_no_login_ass_equipment(self):
        content = encode_multipart('BoUnDaRyStRiNg', {
            'unit_list_id': [self.unit_1.id, self.unit_2.id],
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment/{self.equipment_2.id}/add_equipment_for_unit/',
                               content,
                               content_type=content_type)
        self.assertEqual(resp.status_code, 401)

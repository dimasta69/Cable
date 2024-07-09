import json
from django.test import TestCase
from django.test.client import encode_multipart

from models_app.factories.equipment import EquipmentFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.room import RoomFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.type_port import TypePortFactory
from models_app.factories.user import UserFactory
from models_app.factories.server_rack import ServerRackFactory
from models_app.factories.unit import UnitFactory


class RoomTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.type_port_1 = TypePortFactory.create()
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1)
        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=20,
                                                         type_port=cls.type_port_1)
        cls.equipment_1 = EquipmentFactory.create(template=cls.equipment_template_1)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)

        cls.room_1 = RoomFactory.create(building=cls.building_1, type='Серверная')
        cls.room_2 = RoomFactory.create(building=cls.building_1, type='Серверная')

        cls.server_rack_1 = ServerRackFactory.create(room=cls.room_1, number_of_units=20)

        cls.unit_1 = UnitFactory.create(server_rack=cls.server_rack_1, side='Лицевая', equipment=cls.equipment_1)

    def test_return_200_update_max_params(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'title': 'test_1', 'max_power': 100})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/server_rack/{self.server_rack_1.id}/', content,
                               content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_update_notfound_server_rack(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'title': 'test_1', 'max_power': 100})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put('/core_api/server_rack/99/', content, content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_401_update_not_auth(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'title': 'test_1', 'max_power': 100})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/server_rack/{self.server_rack_1.id}/', content, content_type=content_type)
        self.assertEqual(resp.status_code, 401)

    def test_return_200_get(self):
        resp = self.client.get(f'/core_api/server_rack/{self.server_rack_1.id}/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_get_not_found(self):
        resp = self.client.get('/core_api/server_rack/99/',
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_401_get_not_auth(self):
        resp = self.client.get(f'/core_api/server_rack/{self.server_rack_1.id}/',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_return_204_delete(self):
        resp = self.client.delete(f'/core_api/server_rack/{self.server_rack_1.id}/',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 204)

    def test_return_404_delete_not_found(self):
        resp = self.client.delete('/core_api/server_rack/99/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 404)

    def test_return_401_not_auth(self):
        resp = self.client.delete(f'/core_api/server_rack/{self.server_rack_1.id}/',
                                  content_type='application/json')
        self.assertEqual(resp.status_code, 401)

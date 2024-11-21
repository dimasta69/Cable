from django.test import TestCase

from models_app.factories.access import AccessFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.room import RoomFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.type_port import TypePortFactory
from models_app.factories.user import UserFactory


class CreateEquipmentFromRoomTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)
        cls.user_2 = UserFactory.create(create_token=True)
        cls.user_3 = UserFactory.create(create_token=True)
        cls.user_4 = UserFactory.create(create_token=True)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)
        cls.building_2 = BuildingFactory.create(scheme=cls.scheme_2)

        cls.room_1 = RoomFactory.create(building=cls.building_2, type='Обычная')
        cls.room_2 = RoomFactory.create(building=cls.building_2, type='Серверная')

        cls.access_1 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_1, role='Creator')
        cls.access_2 = AccessFactory.create(scheme=cls.scheme_2, user=cls.user_2, role='Change')
        cls.access_3 = AccessFactory.create(scheme=cls.scheme_2, user=cls.user_3, role='Read')
        cls.access_4 = AccessFactory.create(scheme=cls.scheme_2, user=cls.user_1, role='Creator')

        cls.manufacturer_1 = ManufacturerFactory.create()

        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1, number_of_units=2,
                                                                   power=150)

        cls.type_port_1 = TypePortFactory.create()

        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1, number_of_units=2,
                                                                   power=150)

        cls.type_port_1 = TypePortFactory.create()

        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=20,
                                                         modular=False, type_port=cls.type_port_1)

    def test_return_200_create_equipment(self):
        data = {'equipment_template_id': self.equipment_template_1.id, 'room_id': self.room_1.id}
        resp = self.client.post('/core_api/equipment/create_from_room/', data, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_return_404_equipment_template_not_found(self):
        data = {'equipment_template_id': 99, 'room_id': self.room_1.id}
        resp = self.client.post('/core_api/equipment/create_from_room/', data, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_room_not_found(self):
        data = {'equipment_template_id': self.equipment_template_1.id, 'room_id': 99}
        resp = self.client.post('/core_api/equipment/create_from_room/', data, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_422_room_type_error(self):
        data = {'equipment_template_id': self.equipment_template_1.id, 'room_id': self.room_2.id}
        resp = self.client.post('/core_api/equipment/create_from_room/', data, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_200_create_equipment_role_change(self):
        data = {'equipment_template_id': self.equipment_template_1.id, 'room_id': self.room_1.id}
        resp = self.client.post('/core_api/equipment/create_from_room/', data, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_return_403_create_equipment_role_read(self):
        data = {'equipment_template_id': self.equipment_template_1.id, 'room_id': self.room_1.id}
        resp = self.client.post('/core_api/equipment/create_from_room/', data, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_403_create_equipment_no_role(self):
        data = {'equipment_template_id': self.equipment_template_1.id, 'room_id': self.room_1.id}
        resp = self.client.post('/core_api/equipment/create_from_room/', data, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_4.auth_token}')
        self.assertEqual(resp.status_code, 403)

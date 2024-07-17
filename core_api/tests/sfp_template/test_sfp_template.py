from django.test import TestCase

from models_app.factories.equipment import EquipmentFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.port import PortFactory
from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.type_port import TypePortFactory
from models_app.factories.sfp_template import SfpTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory


class SfpTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()

        cls.type_port_1 = TypePortFactory.create()
        cls.type_port_2 = TypePortFactory.create()

        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1,
                                                                   type='Пассивное оборудование')
        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=7, speed=[1000],
                                                         modular=True, type_port=cls.type_port_1)
        cls.port_template_2 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=7, speed=[10000],
                                                         modular=True, type_port=cls.type_port_1)

        cls.sfp_template_1 = SfpTemplateFactory.create(manufacturer=cls.manufacturer_2, type_port=cls.type_port_1,
                                                       line_type='Многомодовый', speed=[1000])

        cls.equipment_1 = EquipmentFactory.create(template=cls.equipment_template_1)
        cls.equipment_2 = EquipmentFactory.create(template=cls.equipment_template_1)

        cls.port_1 = PortFactory.create(equipment=cls.equipment_1, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_1)
        cls.port_2 = PortFactory.create(equipment=cls.equipment_1, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_1)
        cls.port_3 = PortFactory.create(equipment=cls.equipment_2, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_2)
        cls.port_4 = PortFactory.create(equipment=cls.equipment_2, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_2)

    def test_return_200_min_params(self):
        resp = self.client.delete(f'/core_api/sfp_template/{self.sfp_template_1.id}/', content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 204)

    def test_return_401_not_auth(self):
        resp = self.client.delete(f'/core_api/sfp_template/{self.sfp_template_1.id}/', content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_return_404_sfp_template_not_found(self):
        resp = self.client.delete('/core_api/sfp_template/99/', content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_adding_sfp(self):
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/adding_to_port/',
                               {'port_list': [self.port_1.id, self.port_2.id], 'equipment_id': self.equipment_1.id},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_422_adding_sfp_no_speed(self):
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/adding_to_port/',
                               {'port_list': [self.port_3.id, self.port_4.id], 'equipment_id': self.equipment_2.id},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_200_adding_sfp_equipment_id(self):
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/adding_to_port/',
                               {'port_list': [self.port_1.id, self.port_2.id], 'equipment_id': self.equipment_2.id},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_adding_sfp_equipment_not_found(self):
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/adding_to_port/',
                               {'port_list': [self.port_1.id, self.port_2.id], 'equipment_id': 99},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_adding_sfp_port_not_found(self):
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/adding_to_port/',
                               {'port_list': [self.port_1.id, 99], 'equipment_id': self.equipment_1.id},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_adding_sfp_port_is_not_equipment(self):
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/adding_to_port/',
                               {'port_list': [self.port_1.id, self.port_3.id], 'equipment_id': self.equipment_1.id},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_adding_sfp_speed_mismatch(self):
        resp = self.client.put(f'/core_api/sfp_template/{self.sfp_template_1.id}/adding_to_port/',
                               {'port_list': [self.port_3.id], 'equipment_id': self.equipment_2.id},
                               content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

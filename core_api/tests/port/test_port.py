import json

from django.test import TestCase
from django.test.client import encode_multipart

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.equipment import EquipmentFactory
from models_app.factories.port import PortFactory


class EquipmentListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1,
                                                                   type='Сервер')
        cls.equipment_template_2 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1)
        cls.equipment_template_3 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1,
                                                                   type='Пассивное оборудование')
        cls.equipment_template_4 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1,
                                                                   type='Пассивное оборудование')

        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=20)
        cls.port_template_2 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_2, count=7, speed=[10000])
        cls.port_template_3 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_3, count=7, speed=[10000])
        cls.port_template_4 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_4, count=7, speed=[10000])

        cls.equipment_1 = EquipmentFactory.create(template=cls.equipment_template_1)
        cls.equipment_2 = EquipmentFactory.create(template=cls.equipment_template_2)
        cls.equipment_3 = EquipmentFactory.create(template=cls.equipment_template_3)
        cls.equipment_4 = EquipmentFactory.create(template=cls.equipment_template_4)

        cls.port_1 = PortFactory.create(equipment=cls.equipment_1, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_1)

        cls.port_2 = PortFactory.create(equipment=cls.equipment_1, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_1)

        cls.port_3 = PortFactory.create(equipment=cls.equipment_2, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_2)

        cls.port_4 = PortFactory.create(equipment=cls.equipment_3, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_3)
        cls.port_5 = PortFactory.create(equipment=cls.equipment_3, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_4)

    def test_return_200_update_max_params(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'line_type': 'Одномодовый', 'vlan_type': 'Access',
                                                      'vlan': 1, 'ip': '10.16.7.79', 'mac': 'EE:F8:54:C6:47:E3',
                                                      'connection_id': self.port_2.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_not_found_port(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'line_type': 'Одномодовый', 'vlan_type': 'Access',
                                                      'vlan': 1, 'ip': '10.16.7.79', 'mac': 'EE:F8:54:C6:47:E3',
                                                      'connection_id': self.port_2.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put('/core_api/port/99/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_not_found_connection(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'line_type': 'Одномодовый', 'vlan_type': 'Access',
                                                      'vlan': 1, 'ip': '10.16.7.79', 'mac': 'EE:F8:54:C6:47:E3',
                                                      'connection_id': 99})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_422_speed_error(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'line_type': 'Одномодовый', 'vlan_type': 'Access',
                                                      'vlan': 1, 'ip': '10.16.7.79', 'mac': 'EE:F8:54:C6:47:E3',
                                                      'connection_id': self.port_3.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_200_connection_to_pigtail(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'connection_pigtail_id': self.port_5.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_4.id}/connection_pigtail/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_422_connection_no_type(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'connection_pigtail_id': self.port_4.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_2.id}/connection_pigtail/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

        content = encode_multipart('BoUnDaRyStRiNg', {'connection_pigtail_id': self.port_2.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_4.id}/connection_pigtail/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_connection_pigtail_not_found(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'connection_pigtail_id': 99})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_4.id}/connection_pigtail/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

        content = encode_multipart('BoUnDaRyStRiNg', {'connection_pigtail_id': self.port_4.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put('/core_api/port/99/connection_pigtail/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_401_connection_pigtail_not_auth(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'connection_pigtail_id': self.port_2.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_4.id}/connection_pigtail/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 401)

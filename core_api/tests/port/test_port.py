import json

from django.test import TestCase
from django.test.client import Client, encode_multipart

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.equipment import EquipmentFactory
from models_app.factories.port import PortFactory


class EquipmentListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.client = Client()

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer_1)

        cls.port_template_1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=20)

        cls.equipment_1 = EquipmentFactory.create(template=cls.equipment_template_1)

        cls.port_1 = PortFactory.create(equipment=cls.equipment_1, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_1)

        cls.port_2 = PortFactory.create(equipment=cls.equipment_1, connection=None, vlan_type=None,
                                        line_type=None, ip=None, mac=None,
                                        port_template=cls.port_template_1)

    def test_return_200_update_max_params(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        content = encode_multipart('BoUnDaRyStRiNg', {'line_type': 'Одномодовый', 'vlan_type': 'Access',
                                                      'vlan': 1, 'ip': '10.16.7.79', 'mac': 'EE:F8:54:C6:47:E3',
                                                      'connection_id': self.port_2.id})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/port/{self.port_1.id}/',
                               content, content_type=content_type)
        self.assertEqual(resp.status_code, 200)

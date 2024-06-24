from django.test import TestCase
from django.test.client import Client

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
        cls.port_template_2 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template_1, count=4)

        cls.equipment_1 = EquipmentFactory.create(template=cls.equipment_template_1)

        cls.port_1 = PortFactory.create_batch(20, equipment=cls.equipment_1, connection=None, vlan_type=None,
                                              line_type=None, ip=None, mac=None,
                                              port_template_id=cls.port_template_1.id)
        cls.port_2 = PortFactory.create_batch(4, equipment=cls.equipment_1, connection=None, vlan_type=None,
                                              line_type=None, ip=None, mac=None,
                                              port_template_id=cls.port_template_2.id)

    def test_return_200(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.get(f'/core_api/port/', {'filter_equipment': self.equipment_1.id,
                                                    'order_by': '-uid'})
        self.assertEqual(resp.status_code, 200)

    def test_return_404_equipment_not_found(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.get(f'/core_api/port/', {'filter_equipment':99,
                                                    'order_by': '-uid'})
        self.assertEqual(resp.status_code, 404)

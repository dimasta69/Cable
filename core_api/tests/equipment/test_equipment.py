from django.test import TestCase
from django.test.client import Client, encode_multipart

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory
from models_app.factories.equipment import EquipmentFactory


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
        cls.equipment_2 = EquipmentFactory.create(template=cls.equipment_template_3)
        cls.equipment_3 = EquipmentFactory.create(template=cls.equipment_template_4)

    def test_return_200_get_equipment(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get(f'/core_api/equipment/{self.equipment_3.id}/')
        self.assertEqual(resp.status_code, 200)

    def test_return_404_not_found(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/equipment/99/')
        self.assertEqual(resp.status_code, 404)

    def test_return_204_delete(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.delete(f'/core_api/equipment/{self.equipment_3.id}/')
        self.assertEqual(resp.status_code, 204)

    def test_return_404_delete(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.delete('/core_api/equipment/99/')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_update_change(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        content = encode_multipart('BoUnDaRyStRiNg', {
            'vlan_ip': '{"2": "10.16.7.150"}',
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/equipment/{self.equipment_3.id}/',
                               content,
                               content_type=content_type)
        self.assertEqual(resp.status_code, 200)

    def test_return_404_update_not_found(self):
        content = encode_multipart('BoUnDaRyStRiNg', {
            'vlan_ip': '{"2": "10.16.7.150"}',
        })
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.put('/core_api/equipment/99/', content, content_type=content_type)
        self.assertEqual(resp.status_code, 404)

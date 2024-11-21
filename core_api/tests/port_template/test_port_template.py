from django.test import TestCase
from django.test.client import encode_multipart
import json

from models_app.factories.port_template import PortTemplateFactory
from models_app.factories.type_port import TypePortFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.equipment_template import EquipmentTemplateFactory


class PortTemplateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer = ManufacturerFactory.create()
        cls.equipment_template = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer, number_of_units=1)
        cls.equipment_template_1 = EquipmentTemplateFactory.create(manufacturer=cls.manufacturer)

        cls.type_port_1 = TypePortFactory.create()

        cls.port_template1 = PortTemplateFactory.create(equipment_tmp=cls.equipment_template, type_port=cls.type_port_1,
                                                        lines=2, unit=[1])

    def test_return_200_valid_login(self):
        resp = self.client.get(f'/core_api/port_template/{self.port_template1.id}/',
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_401_no_login(self):
        resp = self.client.get(f'/core_api/port_template/{self.port_template1.id}/')
        self.assertEqual(resp.status_code, 401)

    def test_return_200_change_name(self):
        content = {'name': 'test_1'}
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['name'] == 'test_1')

    def test_return_422_change_valid_name(self):
        content = {'name': self.port_template1.name}
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_found(self):
        resp_get = self.client.get('/core_api/port_template/99/', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        content = encode_multipart('BoUnDaRyStRiNg', {'name': 'test_1'})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp_update = self.client.put('/core_api/port_template/99/',
                                      content, content_type=content_type,
                                      HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_delete = self.client.delete('/core_api/port_template/99/',
                                         HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp_get.status_code, 404)
        self.assertEqual(resp_update.status_code, 404)
        self.assertEqual(resp_delete.status_code, 404)

    def test_return_204_delete(self):
        resp = self.client.delete(f'/core_api/port_template/{self.port_template1.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertTrue(resp.status_code, 204)

    def test_return_422_line_presence(self):
        content = {'lines': 6, 'unit': [1]}
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_422_update_port_template_count_port(self):
        data = {'unit': [1, 2, 3]}
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/', data,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 422)

    def test_return_422_update_port_template_line_presence(self):
        data = {'unit': [1], 'lines': 3}
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/', data,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 422)

    def test_return_200_update_port_template_line_presence(self):
        data = {'unit': [1], 'lines': 2}
        resp = self.client.put(f'/core_api/port_template/{self.port_template1.id}/', data,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 200)

from django.test import TestCase
from django.test.client import Client, encode_multipart
import json

from models_app.factories.manufacturer import ManufacturerFactory
from models_app.factories.user import UserFactory


class ManufacturerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer = ManufacturerFactory.create_batch(20)
        cls.manufacturer_1 = ManufacturerFactory.create()

    def test_return_200_valid_login(self):
        resp = self.client.get(f'/core_api/manufacturer/{self.manufacturer_1.id}/',
                               content_type='application/json', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}'
                               )
        self.assertEqual(resp.status_code, 200)

    def test_return_200_no_login(self):
        resp = self.client.get(f'/core_api/manufacturer/{self.manufacturer_1.id}/',
                               content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_return_200_change_name(self):
        content = {'name': 'test_1'}
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/manufacturer/{self.manufacturer_1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['name'] == 'test_1')

    def test_return_422_change_valid_name(self):
        content = {'name': self.manufacturer_1.name}
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/manufacturer/{self.manufacturer_1.id}/',
                               content, content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_found(self):
        resp_get = self.client.get('/core_api/manufacturer/55/', HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        content = encode_multipart('BoUnDaRyStRiNg', {'name': 'test_1'})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp_update = self.client.put('/core_api/manufacturer/55/',
                                      content, content_type=content_type,
                                      HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_delete = self.client.delete('/core_api/manufacturer/55/',
                                         HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp_get.status_code, 404)
        self.assertEqual(resp_update.status_code, 404)
        self.assertEqual(resp_delete.status_code, 404)

    def test_return_204_delete(self):
        resp = self.client.delete(f'/core_api/manufacturer/{self.manufacturer_1.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertTrue(resp.status_code, 204)

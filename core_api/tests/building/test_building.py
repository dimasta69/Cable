import json
from django.test import TestCase

from models_app.factories.access import AccessFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.user import UserFactory


class BuildingListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)
        cls.user_2 = UserFactory.create(create_token=True)
        cls.user_3 = UserFactory.create(create_token=True)
        cls.user_4 = UserFactory.create(create_token=True)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.access_1 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_1, role='Creator')
        cls.access_2 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_2, role='Change')
        cls.access_3 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_4, role='Read')

        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)
        cls.building_2 = BuildingFactory.create(scheme=cls.scheme_1)

    def test_return_200_update_max_params(self):
        content = {
            'number': 'test',
            'coord_x': 1.22,
            'coord_y': 1.23,
        }
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/building/{self.building_1.id}/',
                               content,
                               content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['number'] == 'test')
        self.assertTrue(resp_json['coord_x'] == 1.22)
        self.assertTrue(resp_json['coord_y'] == 1.23)

    def test_return_422_number_error(self):
        content = {
            'number': self.building_2.number.upper(),
            'coord_x': 1.22,
            'coord_y': 1.23,
        }
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/building/{self.building_1.id}/',
                               content,
                               content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_found(self):
        content = {
            'number': 'test',
            'coord_x': 1.22,
            'coord_y': 1.23,
        }
        content_type = 'application/json'
        resp = self.client.put('/core_api/building/99/',
                               content,
                               content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_204_delete(self):
        resp = self.client.delete(f'/core_api/building/{self.building_1.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 204)

    def test_return_404_delete_not_found(self):
        resp = self.client.delete('/core_api/building/99/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_update_max_params_role_chang(self):
        content = {
            'number': 'test',
            'coord_x': 1.22,
            'coord_y': 1.23,
        }
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/building/{self.building_1.id}/',
                               content,
                               content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['number'] == 'test')
        self.assertTrue(resp_json['coord_x'] == 1.22)
        self.assertTrue(resp_json['coord_y'] == 1.23)

    def test_return_403_not_role(self):
        content = {
            'number': 'test',
            'coord_x': 1.22,
            'coord_y': 1.23,
        }
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/building/{self.building_1.id}/',
                               content,
                               content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_204_delete_role_chang(self):
        resp = self.client.delete(f'/core_api/building/{self.building_1.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 204)

    def test_return_403_delete_no_role(self):
        resp = self.client.delete(f'/core_api/building/{self.building_1.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_403_delete_role_read(self):
        resp = self.client.delete(f'/core_api/building/{self.building_1.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_4.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_403_role_read(self):
        content = {
            'number': 'test',
            'coord_x': 1.22,
            'coord_y': 1.23,
        }
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/building/{self.building_1.id}/',
                               content,
                               content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_4.auth_token}')
        self.assertEqual(resp.status_code, 403)

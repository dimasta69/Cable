import json

from django.test import TestCase
from django.test.client import Client

from models_app.factories.scheme import SchemeFactory
from models_app.factories.access import AccessFactory
from models_app.factories.user import UserFactory


class AccessTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.user_2 = UserFactory.create()
        cls.user_3 = UserFactory.create()
        cls.user_4 = UserFactory.create()
        cls.user_5 = UserFactory.create()

        cls.client = Client()

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.access_1 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_1, role='Creator')
        cls.access_2 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_2, role='Change')
        cls.access_3 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_3, role='Read')
        cls.access_4 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_4, role='Read')

    def test_return_204_delete_access(self):
        resp = self.client.delete(f'/core_api/access/{self.access_2.id}', content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 204)

    def test_return_422_delete_access_creator(self):
        resp = self.client.delete(f'/core_api/access/{self.access_1.id}', content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_403_delete_access_no_creator(self):
        resp = self.client.delete(f'/core_api/access/{self.access_2.id}', content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_404_delete_access_no_found_access(self):
        resp = self.client.delete('/core_api/access/94994', content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_update_access(self):
        content = {'role': 'Read'}
        resp = self.client.put(f'/core_api/access/{self.access_2.id}', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_403_update_access(self):
        content = {'role': 'Read'}
        resp = self.client.put(f'/core_api/access/{self.access_3.id}', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_422_update_access_creator(self):
        content = {'role': 'Read'}
        resp = self.client.put(f'/core_api/access/{self.access_1.id}', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_role_not_found(self):
        content = {'role': '1'}
        resp = self.client.put(f'/core_api/access/{self.access_1.id}', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_role_not_found_access(self):
        content = {'role': '1'}
        resp = self.client.put('/core_api/access/101010', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

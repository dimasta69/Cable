import json

from django.test import TestCase
from django.test.client import Client

from models_app.factories.scheme import SchemeFactory
from models_app.factories.access import AccessFactory
from models_app.factories.user import UserFactory


class AccessListTest(TestCase):
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

    # def test_show_scheme_list_return_200_login(self):
    #     content = {'filter_scheme_id': self.scheme_1.id}
    #     resp = self.client.get(f'/core_api/access/', content, content_type='application/json',
    #                            HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
    #     self.assertEqual(resp.status_code, 200)
    #     resp_json = json.loads(resp.content)
    #     self.assertTrue(len(resp_json['results']) == 4)

    def test_show_scheme_list_return_403_role(self):
        content = {'filter_scheme_id': self.scheme_1.id}
        resp = self.client.get('/core_api/access/', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get('/core_api/access/', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 403)
        resp = self.client.get('/core_api/access/', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_4.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_200_search_filter(self):
        content = {'filter_scheme_id': self.scheme_1.id,
                   'search_filter': self.user_2.username}
        resp = self.client.get('/core_api/access/', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.content)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_return_200_filter_role(self):
        content = {'filter_scheme_id': self.scheme_1.id,
                   'filter_role': "Read"}
        resp = self.client.get('/core_api/access/', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 2)

    def test_show_scheme_list_return_404(self):
        content = {'filter_scheme_id': 11888}
        resp = self.client.get('/core_api/access/', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_show_scheme_list_return_401(self):
        content = {'filter_scheme_id': self.scheme_1.id}
        resp = self.client.get('/core_api/access/', content, content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_show_scheme_list_return_404_filter_role(self):
        content = {'filter_scheme_id': self.scheme_1.id,
                   'filter_role': "1"}
        resp = self.client.get('/core_api/access/', content, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_201_create_access(self):
        content = {'scheme_id': self.scheme_1.id,
                   'user_id': self.user_5.id,
                   'role': 'Read'}
        resp = self.client.post('/core_api/access/', content, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_return_403_create_access_role(self):
        content = {'scheme_id': self.scheme_1.id,
                   'user_id': self.user_5.id,
                   'role': 'Read'}
        resp = self.client.post('/core_api/access/', content, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_422_create_access_return(self):
        content = {'scheme_id': self.scheme_1.id,
                   'user_id': self.user_4.id,
                   'role': 'Read'}
        resp = self.client.post('/core_api/access/', content, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_create_scheme_not_found(self):
        content = {'scheme_id': 11999,
                   'user_id': self.user_5.id,
                   'role': 'Read'}
        resp = self.client.post('/core_api/access/', content, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_create_user_not_found(self):
        content = {'scheme_id': self.scheme_1.id,
                   'user_id': 19000,
                   'role': 'Read'}
        resp = self.client.post('/core_api/access/', content, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_404_create_role_not_found(self):
        content = {'scheme_id': self.scheme_1.id,
                   'user_id': self.user_5.id,
                   'role': '1'}
        resp = self.client.post('/core_api/access/', content, content_type='application/json',
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

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
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_3 = SchemeFactory.create(creator=cls.user_1)
        cls.building_list_1 = BuildingFactory.create_batch(20, scheme=cls.scheme_1)
        cls.building_list_2 = BuildingFactory.create_batch(2, scheme=cls.scheme_2)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_3)

        cls.access_1 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_1, role='Creator')
        cls.access_2 = AccessFactory.create(scheme=cls.scheme_2, user=cls.user_1, role='Creator')
        cls.access_3 = AccessFactory.create(scheme=cls.scheme_3, user=cls.user_1, role='Creator')
        cls.access_4 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_3, role='Read')
        cls.access_5 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_4, role='Change')

    def test_return_200(self):
        resp = self.client.get('/core_api/building/', {'filter_scheme_id': self.scheme_1.id},
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json) == 20)

    def test_return_404_not_found_scheme(self):
        resp = self.client.get('/core_api/building/', {'filter_scheme_id': 99},
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_201_create(self):
        content = {
            'scheme_id': self.scheme_1.id,
            'number': 'test',
        }
        content_type = 'application/json'
        resp = self.client.post('/core_api/building/',
                                content,
                                content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_return_404_create_scheme_not_found(self):
        content = {
            'scheme_id': 99,
            'number': 'test',
        }
        content_type = 'application/json'
        resp = self.client.post('/core_api/building/',
                                content,
                                content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_422_create_scheme_number_repeat(self):
        content = {
            'scheme_id': self.scheme_3.id,
            'number': self.building_1.number.lower(),
        }
        content_type = 'application/json'
        resp = self.client.post('/core_api/building/', content,
                                content_type=content_type,  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_403_not_access(self):
        resp = self.client.get('/core_api/building/', {'filter_scheme_id': self.scheme_1.id},
                               HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_200_read_access(self):
        resp = self.client.get('/core_api/building/', {'filter_scheme_id': self.scheme_1.id},
                               HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json) == 20)

    def test_return_403_not_role(self):
        content = {
            'scheme_id': self.scheme_1.id,
            'number': 'test',
        }
        content_type = 'application/json'
        resp = self.client.post('/core_api/building/',
                                content,
                                content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_403_role_read(self):
        content = {
            'scheme_id': self.scheme_1.id,
            'number': 'test',
        }
        content_type = 'application/json'
        resp = self.client.post('/core_api/building/',
                                content,
                                content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_403_role_change(self):
        content = {
            'scheme_id': self.scheme_1.id,
            'number': 'test',
        }
        content_type = 'application/json'
        resp = self.client.post('/core_api/building/',
                                content,
                                content_type=content_type, HTTP_AUTHORIZATION=f'Token {self.user_4.auth_token}')
        self.assertEqual(resp.status_code, 201)

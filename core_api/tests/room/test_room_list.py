import json
from django.test import TestCase

from models_app.factories.access import AccessFactory
from models_app.factories.room import RoomFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.user import UserFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class RoomListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)
        cls.user_2 = UserFactory.create(create_token=True)
        cls.user_3 = UserFactory.create(create_token=True)
        cls.user_4 = UserFactory.create(create_token=True)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)
        cls.building_2 = BuildingFactory.create(scheme=cls.scheme_2)

        cls.access_1 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_1, role='Creator')
        cls.access_2 = AccessFactory.create(scheme=cls.scheme_2, user=cls.user_1, role='Creator')
        cls.access_3 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_2, role='Change')
        cls.access_4 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_3, role='Read')
        cls.access_5 = AccessFactory.create(scheme=cls.scheme_2, user=cls.user_4, role='Read')

        cls.room_list_1 = RoomFactory.create_batch(18, building=cls.building_1, type='Серверная')
        cls.room_list_2 = RoomFactory.create_batch(2, building=cls.building_1, type='Обычная')
        cls.room_1 = RoomFactory.create(building=cls.building_2, type='Серверная')

    def test_return_200_min_params(self):
        data = {'filter_building_id': self.building_1.id}
        resp = self.client.get('/core_api/room/', data, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 20)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

    def test_return_401_no_login(self):
        resp = self.client.get('/core_api/room/', content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_return_404_building_not_found(self):
        data = {'filter_building_id': 99}
        resp = self.client.get('/core_api/room/', data, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_filter_type(self):
        data = {'filter_building_id': self.building_1.id, 'filter_type': 'Обычная'}
        resp = self.client.get('/core_api/room/', data, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 2)

    def test_return_200_search_filter(self):
        data = {'filter_building_id': self.building_2.id, 'search_filter': self.room_1.number}
        resp = self.client.get('/core_api/room/', data, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json['results']) == 1)

    def test_return_201_create_room(self):
        data = {'building_id': self.building_2.id, 'number': 'wed', 'type': 'Серверная'}
        resp = self.client.post('/core_api/room/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_return_404_create_not_found_building(self):
        data = {'building_id': 99, 'number': 'wed', 'type': 'Серверная'}
        resp = self.client.post('/core_api/room/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_422_number_retry(self):
        data = {'building_id': self.building_2.id, 'number': self.room_1.number, 'type': 'Серверная'}
        resp = self.client.post('/core_api/room/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_200_role_change(self):
        data = {'filter_building_id': self.building_1.id}
        resp = self.client.get('/core_api/room/', data, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_200_role_read(self):
        data = {'filter_building_id': self.building_1.id}
        resp = self.client.get('/core_api/room/', data, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_403_no_role(self):
        data = {'filter_building_id': self.building_1.id}
        resp = self.client.get('/core_api/room/', data, content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_4.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_201_role_change(self):
        data = {'building_id': self.building_1.id, 'number': 'wed', 'type': 'Серверная'}
        resp = self.client.post('/core_api/room/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_2.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_return_403_role_read(self):
        data = {'building_id': self.building_1.id, 'number': 'wed', 'type': 'Серверная'}
        resp = self.client.post('/core_api/room/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_3.auth_token}')
        self.assertEqual(resp.status_code, 403)

    def test_return_403_no_role_create(self):
        data = {'building_id': self.building_1.id, 'number': 'wed', 'type': 'Серверная'}
        resp = self.client.post('/core_api/room/', data,
                                HTTP_AUTHORIZATION=f'Token {self.user_4.auth_token}')
        self.assertEqual(resp.status_code, 403)

import json
from django.test import TestCase

from models_app.factories.room import RoomFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.user import UserFactory
from models_app.factories.server_rack import ServerRackFactory


class RoomTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)

        cls.room_1 = RoomFactory.create(building=cls.building_1, type='Серверная')
        cls.room_2 = RoomFactory.create(building=cls.building_1, type='Серверная')
        cls.room_3 = RoomFactory.create(building=cls.building_1, type='Обычная')

        cls.server_rack_list_1 = ServerRackFactory.create_batch(4, room=cls.room_1)
        cls.server_rack_1 = ServerRackFactory.create(room=cls.room_1)
        cls.server_rack_list_2 = ServerRackFactory.create_batch(6, room=cls.room_2)

    def test_return_200(self):
        resp = self.client.get('/core_api/server_rack/', {'filter_room_id': self.room_1.id},
                               content_type={'application/json'},
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json) == 5)

    def test_return_404_not_found_room(self):
        resp = self.client.get('/core_api/server_rack/', {'filter_room_id': 99}, content_type={'application/json'},
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_200_order_by(self):
        resp = self.client.get('/core_api/server_rack/', {'filter_room_id': self.room_1.id, 'order_by': 'title'},
                               content_type={'application/json'},
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json) == 5)

    def test_return_200_search_filter(self):
        resp = self.client.get('/core_api/server_rack/', {'filter_room_id': self.room_1.id,
                                                          'search_filter': self.server_rack_1.title},
                               content_type={'application/json'},
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp_json) == 1)

    def test_return_401_not_auth(self):
        resp = self.client.get('/core_api/server_rack/', {'filter_room_id': self.room_1.id,
                                                          'search_filter': self.server_rack_1.title},
                               content_type={'application/json'})
        self.assertEqual(resp.status_code, 401)

    def test_return_201_create_stack(self):
        resp = self.client.post('/core_api/server_rack/', {'number_of_units': 20, 'room_id': self.room_1.id,
                                                           'title': 'sfds', 'mac_power': 200},
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 201)

    def test_return_404_create_not_found_room(self):
        resp = self.client.post('/core_api/server_rack/', {'number_of_units': 20, 'room_id': 99,
                                                           'title': 'sfds', 'mac_power': 200},
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_422_room_not_server(self):
        resp = self.client.post('/core_api/server_rack/', {'number_of_units': 20, 'room_id': self.room_3.id,
                                                           'title': 'sfds', 'mac_power': 200},
                                HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

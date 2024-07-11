from django.test import TestCase
from django.test.client import encode_multipart

from models_app.factories.room import RoomFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.user import UserFactory


class RoomTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)
        cls.building_2 = BuildingFactory.create(scheme=cls.scheme_2)

        cls.room_1 = RoomFactory.create(building=cls.building_2, type='Серверная')
        cls.room_2 = RoomFactory.create(building=cls.building_2, type='Серверная')

    def test_return_200_update(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'number': 'sadad'})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/room/{self.room_1.id}/', content, content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 200)

    def test_return_401_not_auth(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'number': 'sadad'})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/room/{self.room_1.id}/', content, content_type=content_type)
        self.assertEqual(resp.status_code, 401)

    def test_return_422_number_retry(self):
        content = {'number': self.room_1.number}
        content_type = 'application/json'
        resp = self.client.put(f'/core_api/room/{self.room_2.id}/', content, content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_found_room(self):
        content = encode_multipart('BoUnDaRyStRiNg', {'number': self.room_1.number})
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put('/core_api/room/99/', content, content_type=content_type,
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_204_delete_room(self):
        resp = self.client.delete(f'/core_api/room/{self.room_2.id}/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 204)

    def test_return_404_delete_not_found_room(self):
        resp = self.client.delete('/core_api/room/99/',
                                  HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        self.assertEqual(resp.status_code, 404)

    def test_return_401_delete_not_auth(self):
        resp = self.client.delete(f'/core_api/room/{self.room_2.id}/')
        self.assertEqual(resp.status_code, 401)

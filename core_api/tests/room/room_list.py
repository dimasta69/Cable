import json
from django.test import TestCase

from models_app.factories.room import RoomFactory
from models_app.factories.building import BuildingFactory
from models_app.factories.scheme import SchemeFactory
from models_app.factories.user import UserFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class RoomListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_1)
        cls.building_1 = BuildingFactory.create(scheme=cls.scheme_1)
        cls.building_2 = BuildingFactory.create(scheme=cls.scheme_2)

        cls.room_list_1 = RoomFactory.create_batch(18, building=cls.building_1, type='Серверная')
        cls.room_list_2 = RoomFactory.create_batch(2, building=cls.building_1, type='Обычная')
        cls.room_list_3 = RoomFactory.create_batch(3, building=cls.building_2, type='Серверная')

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

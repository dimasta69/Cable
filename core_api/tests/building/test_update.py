from django.test import TestCase

import json
from models_app.factories.building import BuildingFactory


class UpdateBuildingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.building = BuildingFactory()

    def test_update_building_full_params_return_200(self):
        update_data = {
            'name': 'new_name',
            'coord_x': 1,
            'coord_y': 1,
        }
        resp = self.client.put(
            f'/core_api/building/{self.building.id}/',
            data=update_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f'Token {self.building.scheme.creator.access_token}',
        )
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            resp_json['name'] == update_data['name'] and
            resp_json['coord_x'] == update_data['coord_x'] and
            resp_json['coord_y'] == update_data['coord_y'],
        )

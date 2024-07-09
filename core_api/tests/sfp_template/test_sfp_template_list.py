import json
from django.test import TestCase

from models_app.factories.type_port import TypePortFactory
from models_app.factories.sfp_template import SfpTemplateFactory
from models_app.factories.user import UserFactory
from models_app.factories.manufacturer import ManufacturerFactory
from cabel.settings.rest_framework import REST_FRAMEWORK


class PortTemplateListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create(create_token=True)

        cls.manufacturer_1 = ManufacturerFactory.create()
        cls.manufacturer_2 = ManufacturerFactory.create()

        cls.type_port_1 = TypePortFactory.create()
        cls.type_port_2 = TypePortFactory.create()

        cls.sfp_template_list_1 = SfpTemplateFactory.create_batch(15, manufacturer=cls.manufacturer_1,
                                                                  type_port=cls.type_port_1, line_type='Многомодовый')
        cls.sfp_template_list_2 = SfpTemplateFactory.create_batch(6, manufacturer=cls.manufacturer_2,
                                                                  type_port=cls.type_port_1, line_type='Одномодовый')

    def test_return_200_min_params(self):
        resp = self.client.get('/core_api/sfp_template/', content_type='application/json',
                               HTTP_AUTHORIZATION=f'Token {self.user_1.auth_token}')
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['pagination']['current_page'] == 1)
        self.assertTrue(resp_json['pagination']['next_page'] == 2)
        self.assertTrue(resp_json['pagination']['per_page'] == REST_FRAMEWORK['PAGE_SIZE'])
        self.assertTrue(resp_json['pagination']['total_count'] == 21)
        self.assertTrue(len(resp_json['results']) == REST_FRAMEWORK['PAGE_SIZE'])

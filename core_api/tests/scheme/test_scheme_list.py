import json

from django.test import TestCase
from django.contrib.auth.hashers import make_password
from django.test.client import Client

from models_app.factories.scheme import SchemeFactory
from models_app.factories.access import AccessFactory
from models_app.factories.user import UserFactory


class SchemeListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.user_2 = UserFactory.create()

        cls.client = Client()

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.access_1 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_1, role='Creator')

    def test_show_scheme_list_return_200_login(self):
        self.client.login(username=self.user_1.username, password="Dima2012")
        resp = self.client.get('/core_api/scheme/', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.content)
        self.assertTrue(len(resp_json) == 1)

    def test_show_scheme_list_return_200_no_valid_login(self):
        self.client.login(username=self.user_2.username, password="Dima2012")
        resp = self.client.get('/core_api/scheme/', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        resp_json = json.loads(resp.content)
        self.assertTrue(len(resp_json) == 0)

    def test_show_scheme_list_return_200_no_login(self):
        resp = self.client.get('/core_api/scheme/', content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_create_scheme_return_201(self):
        self.client.login(username=self.user_2.username, password="Dima2012")
        params = {'title': 'test_1'}
        resp = self.client.post('/core_api/scheme/', params)
        self.assertEqual(resp.status_code, 201)

    def test_no_create_warning_title_return_403(self):
        self.client.login(username=self.user_2.username, password="Dima2012")
        params = {'title': 'test_1'}
        resp_1 = self.client.post('/core_api/scheme/', params)
        self.assertEqual(resp_1.status_code, 201)

        self.client.login(username=self.user_1.username, password="Dima2012")
        params = {'title': 'Test_1'}
        resp_2 = self.client.post('/core_api/scheme/', params)
        self.assertEqual(resp_2.status_code, 403)

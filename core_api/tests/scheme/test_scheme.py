from django.test import TestCase
from django.test.client import Client, encode_multipart

from models_app.factories.scheme import SchemeFactory
from models_app.factories.access import AccessFactory
from models_app.factories.user import UserFactory

import json


class SchemeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = UserFactory.create()
        cls.user_2 = UserFactory.create()

        cls.client = Client()

        cls.scheme_1 = SchemeFactory.create(creator=cls.user_1)
        cls.scheme_2 = SchemeFactory.create(creator=cls.user_2)
        cls.access_1 = AccessFactory.create(scheme=cls.scheme_1, user=cls.user_1, role='Creator')

    def test_show_scheme_200_login(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.get(f'/core_api/scheme/{self.scheme_1.id}/')
        self.assertEqual(resp.status_code, 200)

    def test_show_scheme_403_no_valid_login(self):
        self.client.login(username=self.user_2.username, password='Dima2012')
        resp = self.client.get(f'/core_api/scheme/{self.scheme_1.id}/')
        self.assertEqual(resp.status_code, 403)

    def test_delete_scheme_return_204_login(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.delete(f'/core_api/scheme/{self.scheme_1.id}/')
        self.assertEqual(resp.status_code, 204)

    def test_delete_scheme_return_403_no_valid_login(self):
        self.client.login(username=self.user_2.username, password='Dima2012')
        resp = self.client.delete(f'/core_api/scheme/{self.scheme_1.id}/')
        self.assertEqual(resp.status_code, 403)

    def test_update_scheme_return_200_valid_login(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        data = {'title': 'title113'}
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/scheme/{self.scheme_1.id}/',
                               content,
                               content_type=content_type)
        resp_json = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp_json['title'] == 'title113')

    def test_update_scheme_return_403_no_valid_login(self):
        self.client.login(username=self.user_2.username, password='Dima2012')
        data = {'title': 'title113'}
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/scheme/{self.scheme_1.id}/',
                               content,
                               content_type=content_type)
        self.assertEqual(resp.status_code, 403)

    def test_update_scheme_duplicate_title_return_400_valid_login(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        data = {'title': self.scheme_2.title}
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'
        resp = self.client.put(f'/core_api/scheme/{self.scheme_1.id}/',
                               content,
                               content_type=content_type)
        self.assertEqual(resp.status_code, 422)

    def test_return_404_not_found(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp_get = self.client.get('/core_api/scheme/55/')
        resp_delete = self.client.delete('/core_api/scheme/55/')
        resp_update = self.client.put('core_api/scheme/55/')
        self.assertEqual(resp_delete.status_code, 404)
        self.assertEqual(resp_get.status_code, 404)
        self.assertEqual(resp_update.status_code, 404)

    def test_return_204_delete(self):
        self.client.login(username=self.user_1.username, password='Dima2012')
        resp = self.client.delete(f'/core_api/manufacturer/{self.scheme_1.id}/')
        self.assertTrue(resp.status_code, 204)

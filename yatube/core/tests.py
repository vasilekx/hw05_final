# cores/tests.py

from django.test import TestCase


NONEXISTENT_URL = '/nonexistent_page/'


class ViewTestClass(TestCase):

    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

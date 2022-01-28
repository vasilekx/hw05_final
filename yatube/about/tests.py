# about/tests.py

from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_author_page(self):
        """Проверка доступности адресов приложения about"""
        for value in StaticURLTests.templates_url_names.keys():
            with self.subTest(value=value):
                self.assertEqual(
                    self.guest_client.get(value).status_code,
                    HTTPStatus.OK
                )

    def test_about_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for value, expected in StaticURLTests.templates_url_names.items():
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    self.guest_client.get(value),
                    expected
                )


class StaticViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.templates_pages_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи кода к адресам приложения"""
        for reverse_name in StaticViewsTests.templates_pages_names.keys():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(
                    self.guest_client.get(reverse_name).status_code,
                    HTTPStatus.OK
                )

    def test_about_page_uses_correct_template(self):
        """При запросе к адресам приложения применяется соответствующий
        шаблон"""
        for (
                reverse_name,
                template
        ) in StaticViewsTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.guest_client.get(reverse_name),
                    template
                )

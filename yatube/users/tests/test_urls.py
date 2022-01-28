# users/tests/test_urls.py

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Неавторизованный пользователя
        self.guest_client = Client()
        # Авторизиованный пользователь
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_url_accessible_everyone_user(self):
        """Страницы доступны любому пользователю."""
        urls_available_to_everyone = [
            '/auth/logout/',
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
        ]
        for value in urls_available_to_everyone:
            self.assertEqual(
                self.guest_client.get(value).status_code,
                HTTPStatus.OK
            )

    def test_pages_url_accessible_authorized_user(self):
        """Страницы доступны авторизиованному пользователю."""
        urls_available_authorized_user = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for value in urls_available_authorized_user:
            self.assertEqual(
                self.authorized_client.get(value).status_code,
                HTTPStatus.OK
            )

    def test_pages_url_redirect_anonymous_on_auth_login(self):
        """Перенаправление анонимного пользователя на страницу логина"""
        self.assertRedirects(
            self.guest_client.get('/auth/password_change/', follow=True),
            '/auth/login/?next=/auth/password_change/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/NQ/5x7-216030d3824f05717f53/':
                'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(
                    self.authorized_client.get(adress),
                    template
                )

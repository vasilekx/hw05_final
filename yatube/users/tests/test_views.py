# users/tests/test-views.py

from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UsersViewsTests(TestCase):
    def setUp(self):
        # Авторизиованный пользователь
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_page_uses_correct_template(self):
        """При запросе к адресам приложения применяется соответствующий
        шаблон"""
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change_form'):
                'users/password_change_form.html',
            reverse('users:password_change_done'):
                'users/password_change_done.html',
            reverse('users:password_reset_form'):
                'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'NQ', 'token': '5x7-216030d3824f05717f53'}
            ): 'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
                'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertTemplateUsed(
                    self.authorized_client.get(reverse_name),
                    template
                )

    def test_pages_show_correct_context_form_on_pages(self):
        """Типы полей форм соответсвуют ожиданиям"""
        templates_pages_names = {
            reverse('users:signup'): {
                'first_name': forms.fields.CharField,
                'last_name': forms.fields.CharField,
                'username': forms.fields.CharField,
                'email': forms.fields.EmailField,
                'password1': forms.fields.CharField,
                'password2': forms.fields.CharField,
            },
        }
        for page, form_fields in templates_pages_names.items():
            response = self.authorized_client.get(page)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    self.assertIsInstance(
                        response.context.get('form').fields.get(value),
                        expected
                    )

# users/tests/test_forms.py

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class CreateUserTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """Регистрация создает пользователя"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'name1',
            'last_name': 'name2',
            'username': 'test_username',
            'email': 'test_email@test.test',
            'password1': 'gvog7q~7E',
            'password2': 'gvog7q~7E',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='test_username',
                first_name='name1',
                last_name='name2',
                email='test_email@test.test'
            ).exists()
        )

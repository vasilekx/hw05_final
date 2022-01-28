# posts/tests/test_models.py

from django.test import TestCase

from ..models import Group, Post, User, Follow


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.another_user = User.objects.create_user(username='another_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.follow = Follow.objects.create(
            user=cls.another_user,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:15], str(self.post))
        self.assertEqual(self.group.title, str(self.group))
        self.assertEqual(
            '{} followed {}'.format(self.another_user, self.user),
            str(self.follow)
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post_field_verboses = {
            'text': 'Текст',
            'created': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in post_field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).verbose_name,
                    expected
                )
        group_field_verboses = {
            'title': 'Название',
            'slug': 'Короткая метка',
            'description': 'Описание',
        }
        for value, expected in group_field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).verbose_name,
                    expected
                )
        follow_field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in follow_field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Follow._meta.get_field(value).verbose_name,
                    expected
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post_field_help_texts = {
            'text': 'Текст поста',
            'created': ('Дата создания будет автоматически установлена '
                         'в текущую дату при создании'),
            'author': 'Автор, к которому будет относиться пост',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in post_field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Post._meta.get_field(value).help_text,
                    expected
                )
        group_field_help_texts = {
            'title': 'Дайте короткое название группе',
            'slug': ('Укажите адрес для страницы задачи. Используйте только '
                     'латиницу, цифры, дефисы и знаки подчёркивания'),
            'description': 'Опишите суть группы',
        }
        for value, expected in group_field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Group._meta.get_field(value).help_text,
                    expected
                )
        follow_field_help_texts = {
            'user': 'Пользователь, который подписывается',
            'author': 'Пользователь, на которого подписываются',
        }
        for value, expected in follow_field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    Follow._meta.get_field(value).help_text,
                    expected
                )

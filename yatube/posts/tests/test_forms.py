# posts/tests/test_forms.py

import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, User, Comment
from ..urls import app_name

USERNAME = 'test_user'
USERNAME_AUTH = 'test_auth_user'
POST_TEXT = 'Тестовый текст'
ANOTHER_POST_TEXT = 'Тестовый текст с изменения'
COMMENT_TEXT = 'Тестовый комметарий'

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
ANOTHER_GROUP_TITLE = 'Тестовая группа'
ANOTHER_GROUP_SLUG = 'test-another-slug'
ANOTHER_GROUP_DESCRIPTION = 'Тестовое описание'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_AUTH_URL = reverse(
    'posts:profile',
    args=[USERNAME_AUTH]
)
POST_CREATE_URL = reverse('posts:post_create')
REDIRECTS_POST_CREATE_URL = (f'{reverse(settings.LOGIN_URL)}'
                             f'?next={POST_CREATE_URL}')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
IMAGE_FILE_NAME = 'small.gif'
NEW_IMAGE_FILE_NAME = 'new_small.gif'
ANOTHER_IMAGE_FILE_NAME = 'another_small.gif'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.user_auth = User.objects.create_user(username=USERNAME_AUTH)
        cls.another = Client()
        cls.another.force_login(cls.user_auth)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.another_group = Group.objects.create(
            title=ANOTHER_GROUP_TITLE,
            slug=ANOTHER_GROUP_SLUG,
            description=ANOTHER_GROUP_DESCRIPTION,
        )
        cls.uploaded_file = SimpleUploadedFile(
            name=IMAGE_FILE_NAME,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.uploaded_new_file = SimpleUploadedFile(
            name=NEW_IMAGE_FILE_NAME,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.uploaded_another_file = SimpleUploadedFile(
            name=ANOTHER_IMAGE_FILE_NAME,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded_file
        )
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.COMMENT_CREATE_URL = reverse(
            'posts:add_comment',
            args=[cls.post.pk]
        )
        cls.REDIRECTS_POST_EDIT_URL = (f'{reverse(settings.LOGIN_URL)}'
                                       f'?next={cls.POST_EDIT_URL}')
        cls.REDIRECTS_COMMENT_CREATE_URL = (f'{reverse(settings.LOGIN_URL)}'
                                            f'?next={cls.COMMENT_CREATE_URL}')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def tearDown(self):
        self.uploaded_file.seek(0)
        self.uploaded_new_file.seek(0)
        self.uploaded_another_file.seek(0)

    def test_create_post(self):
        """Валидная форма создает пост."""
        posts_count = Post.objects.count()
        all_posts = set(Post.objects.all())
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': self.uploaded_new_file,
        }
        response = self.another.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            PROFILE_AUTH_URL
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        posts = set(Post.objects.all()) - all_posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user_auth)
        self.assertEqual(post.image,
                         (f"{Post.image.field.upload_to}"
                          f"{form_data['image'].name}"))

    def test_cant_create_post_by_guest(self):
        """Аноним не создает пост."""
        all_posts = set(Post.objects.all())
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': self.uploaded_another_file,
        }
        response = self.guest.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            REDIRECTS_POST_CREATE_URL
        )
        self.assertFalse(set(Post.objects.all()) - all_posts)

    def test_change_post(self):
        """Валидная форма изменяет пост."""
        form_data = {
            'text': ANOTHER_POST_TEXT,
            'group': self.another_group.id,
            'image': self.uploaded_another_file,
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.POST_DETAIL_URL
        )
        post = response.context['post']
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.image, f"{app_name}/{form_data['image'].name}")

    def test_cant_change_post_by_another_author(self):
        """Пользоветель не являющийся автором не изменяет чужой пост."""
        cases = [
            [self.another, PROFILE_AUTH_URL],
            [self.guest, self.REDIRECTS_POST_EDIT_URL]
        ]
        for client, url_redirection in cases:
            with self.subTest(client=client, url_redirection=url_redirection):
                form_data = {
                    'text': ANOTHER_POST_TEXT,
                    'group': self.another_group.id,
                    'image': self.uploaded_another_file,
                }
                response = client.post(
                    self.POST_EDIT_URL,
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(
                    response,
                    url_redirection
                )
                post = Post.objects.get(pk=self.post.pk)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.image, self.post.image)

    def test_create_comment(self):
        """Валидная форма создает комментарий."""
        comments_count = Comment.objects.count()
        all_comments = set(Comment.objects.all())
        form_data = {'text': COMMENT_TEXT}
        response = self.another.post(
            self.COMMENT_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.POST_DETAIL_URL
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        comments = set(Comment.objects.all()) - all_comments
        self.assertEqual(len(comments), 1)
        comment = comments.pop()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user_auth)
        self.assertEqual(comment.post, self.post)

    def test_cant_create_comment_by_guest(self):
        """Аноним не создает комментарий."""
        all_comments = set(Comment.objects.all())
        form_data = {'text': COMMENT_TEXT}
        response = self.guest.post(
            self.COMMENT_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.REDIRECTS_COMMENT_CREATE_URL
        )
        self.assertFalse(set(Comment.objects.all()) - all_comments)

    def test_pages_show_correct_context(self):
        """Проверка типов полей формы для создания и редактирование поста
        соответсвуют ожиданиям"""
        templates_page_names = [
            self.POST_EDIT_URL,
            POST_CREATE_URL
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for page in templates_page_names:
            response = self.author.get(page)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    self.assertIsInstance(
                        response.context.get('form').fields.get(value),
                        expected
                    )

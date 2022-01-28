# posts/tests/test_forms.py

import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm, CommentForm
from ..models import Post, Group, User, Comment

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

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
IMAGE_FILE_NAME = 'small.gif'
ANOTHER_IMAGE_FILE_NAME = 'small.gif'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
ANOTHER_SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x00\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username=USERNAME_AUTH)
        cls.user = User.objects.create_user(username=USERNAME)
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

    # @classmethod
    # def tearDownClass(cls):
    #     super().tearDownClass()
    #     shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.another = Client()
        self.another.force_login(self.user_auth)
        self.author = Client()
        self.author.force_login(self.user)

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает пост."""
        posts_count = Post.objects.count()
        all_posts = set(Post.objects.all())
        uploaded_file = SimpleUploadedFile(
            name=ANOTHER_IMAGE_FILE_NAME,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': uploaded_file,
        }
        self.assertTrue(PostForm(data=form_data).is_valid())
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
        self.assertEqual(post.image, f"posts/{form_data['image'].name}")

    def test_change_post(self):
        """Валидная форма изменяет пост."""
        uploaded_another_file = SimpleUploadedFile(
            name=ANOTHER_IMAGE_FILE_NAME,
            content=ANOTHER_SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': ANOTHER_POST_TEXT,
            'group': self.another_group.id,
            'image': uploaded_another_file,
        }
        self.assertTrue(PostForm(data=form_data).is_valid())
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
        self.assertEqual(post.image, f"posts/{form_data['image'].name}")

    def test_cant_change_post_by_another_author(self):
        """Пользоветель не изменяет чужой пост."""
        uploaded_another_file = SimpleUploadedFile(
            name=IMAGE_FILE_NAME,
            content=ANOTHER_SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': ANOTHER_POST_TEXT,
            'group': self.another_group.id,
            'image': uploaded_another_file,
        }
        response = self.another.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            PROFILE_AUTH_URL
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
        self.assertTrue(CommentForm(data=form_data).is_valid())
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

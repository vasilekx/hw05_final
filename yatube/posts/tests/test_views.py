# posts/tests/test_views.py

import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, User, Comment, Follow
from ..settings import POSTS_PER_PAGE

USERNAME = 'test_user'
USERNAME_AUTH = 'test_auth_user'
POST_TEXT = 'Тестовый текст'
COMMENT_TEXT = 'Тестовый комметарий'

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'
ANOTHER_GROUP_TITLE = 'Тестовая группа'
ANOTHER_GROUP_SLUG = 'test-another-slug'
ANOTHER_GROUP_DESCRIPTION = 'Тестовое описание'

INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
ANOTHER_GROUP_LIST_URL = reverse('posts:group_list', args=[ANOTHER_GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])

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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
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
        cls.another_post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user_auth,
            group=cls.group,
            image=cls.uploaded_file
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text=COMMENT_TEXT,
        )
        cls.follow = Follow.objects.create(user=cls.user, author=cls.user_auth)
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest = Client()
        self.another = Client()
        self.another.force_login(self.user_auth)
        self.author = Client()
        self.author.force_login(self.user)

    def test_post_show_correct_context_on_different_places(self):
        """Пост появился на соответствующих страницах."""
        cases_page_names = [
            [INDEX_URL, 'page_obj', self.post],
            [FOLLOW_INDEX_URL, 'page_obj', self.another_post],
            [GROUP_LIST_URL, 'page_obj', self.post],
            [PROFILE_URL, 'page_obj', self.post],
            [self.POST_DETAIL_URL, 'post', self.post]
        ]
        for url, obj, expected_post in cases_page_names:

            with self.subTest(url=url, obj=obj, expected_post=expected_post):
                response = self.author.get(url)
                if obj == 'page_obj':
                    posts_list = response.context[obj].object_list
                    self.assertEqual(posts_list.count(expected_post), 1)
                    post_index = posts_list.index(expected_post)
                    post = posts_list.pop(post_index)
                elif obj == 'post':
                    post = response.context[obj]
                self.assertEqual(post.pk, expected_post.pk)
                self.assertEqual(post.text, expected_post.text)
                self.assertEqual(post.author, expected_post.author)
                self.assertEqual(post.group, expected_post.group)
                self.assertEqual(post.image, expected_post.image)

    def test_post_not_exist_in_other_group(self):
        """Пост не попал в группу, для которой не был предназначен"""
        self.assertNotIn(
            self.post,
            self.author.get(ANOTHER_GROUP_LIST_URL).context['page_obj']
        )

    def test_post_not_exist_in_other_follows(self):
        """Пост не попал в избранное, для которой не был предназначен"""
        self.assertNotIn(
            self.post,
            self.another.get(FOLLOW_INDEX_URL).context['page_obj']
        )

    def test_author_on_profile_page(self):
        """Автор на соответствующей странице"""
        self.assertEqual(
            self.another.get(PROFILE_URL).context.get('author'),
            self.user
        )

    def test_group_on_group_list(self):
        """Группа на соответствующей странице"""
        group = self.another.get(GROUP_LIST_URL).context['group']
        self.assertEqual(group.pk, self.group.pk)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_comment_on_post_detail(self):
        """Комментарий на соответствующей странице"""
        post = self.another.get(self.POST_DETAIL_URL).context['post']
        comments = post.comments.all()
        self.assertEqual(len(comments), 1)
        comment = comments[0]
        self.assertEqual(comment.post, self.comment.post)
        self.assertEqual(comment.author, self.comment.author)
        self.assertEqual(comment.text, self.comment.text)

    def test_user_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться на
        других пользователей и удалять их из подписок"""
        follow_count = Follow.objects.count()
        all_followers = set(Follow.objects.all())
        response_follow = self.another.get(PROFILE_FOLLOW_URL)
        self.assertRedirects(response_follow, PROFILE_URL)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        followers = set(Follow.objects.all()) - all_followers
        self.assertEqual(len(followers), 1)
        follower = followers.pop()
        self.assertEqual(follower.user, self.user_auth)
        self.assertEqual(follower.author, self.user)
        response_unfollow = self.another.get(PROFILE_UNFOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertRedirects(response_unfollow, PROFILE_URL)
        self.assertNotIn(follower, Follow.objects.all())

    def test_author_cant_follow_and_unfollow_yourself(self):
        follow_count = Follow.objects.count()
        response_follow = self.author.get(PROFILE_FOLLOW_URL)
        self.assertRedirects(response_follow, PROFILE_URL)
        self.assertEqual(Follow.objects.count(), follow_count)
        response_unfollow = self.another.get(PROFILE_UNFOLLOW_URL)
        self.assertRedirects(response_unfollow, PROFILE_URL)
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_page_contains_records(self):
        """Тестирование паджинатора. Количество постов на странице"""
        Post.objects.all().delete()
        num_objects = POSTS_PER_PAGE * 2
        Post.objects.bulk_create(
            [
                Post(
                    text=f'{POST_TEXT}{count}',
                    author=self.user,
                    group=self.group
                )
                for count in range(num_objects)
            ]
        )
        cases = [
            [INDEX_URL, POSTS_PER_PAGE],
            [GROUP_LIST_URL, POSTS_PER_PAGE],
            [PROFILE_URL, POSTS_PER_PAGE],
            [f'{INDEX_URL}?page=2', num_objects - POSTS_PER_PAGE],
            [f'{GROUP_LIST_URL}?page=2', num_objects - POSTS_PER_PAGE],
            [f'{PROFILE_URL}?page=2', num_objects - POSTS_PER_PAGE],
        ]
        for address, expect in cases:
            with self.subTest(address=address, expect=expect):
                self.assertEqual(
                    len(self.guest.get(address).context['page_obj']),
                    expect
                )

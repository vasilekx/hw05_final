# posts/tests/test_urls.py

from http.client import OK, FOUND, NOT_FOUND

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User, Follow

USERNAME = 'test_user'
USERNAME_AUTH = 'test_auth_user'
POST_TEXT = 'Тестовый текст'

GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DESCRIPTION = 'Тестовое описание'

INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
POST_CREATE_URL = reverse('posts:post_create')
REDIRECTS_POST_CREATE_URL = (f'{reverse(settings.LOGIN_URL)}'
                             f'?next={POST_CREATE_URL}')
GROUP_LIST_URL = reverse('posts:group_list', args=[GROUP_SLUG])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
PROFILE_AUTH_URL = reverse(
    'posts:profile',
    args=[USERNAME_AUTH]
)
PROFILE_FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
REDIRECTS_PROFILE_FOLLOW_URL = (f'{reverse(settings.LOGIN_URL)}'
                                f'?next={PROFILE_FOLLOW_URL}')
PROFILE_UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])
REDIRECTS_PROFILE_UNFOLLOW_URL = (f'{reverse(settings.LOGIN_URL)}'
                                  f'?next={PROFILE_UNFOLLOW_URL}')
NONEXISTENT_URL = '/nonexistent_page/'


class StaticURLTests(TestCase):
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
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group
        )
        cls.follow = Follow.objects.create(user=cls.user_auth, author=cls.user)
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.REDIRECTS_POST_EDIT_URL = (f'{reverse(settings.LOGIN_URL)}'
                                       f'?next={cls.POST_EDIT_URL}')

    def test_pages_url_accessible(self):
        """URL-адреса страниц совпадает с ожидаемым доступом."""
        cases = [
            [INDEX_URL, self.guest, OK],
            [GROUP_LIST_URL, self.guest, OK],
            [PROFILE_URL, self.guest, OK],
            [self.POST_DETAIL_URL, self.guest, OK],
            [POST_CREATE_URL, self.guest, FOUND],
            [POST_CREATE_URL, self.another, OK],
            [self.POST_EDIT_URL, self.guest, FOUND],
            [self.POST_EDIT_URL, self.another, FOUND],
            [self.POST_EDIT_URL, self.author, OK],
            [NONEXISTENT_URL, self.guest, NOT_FOUND],
            [PROFILE_FOLLOW_URL, self.guest, FOUND],
            [PROFILE_FOLLOW_URL, self.another, FOUND],
            [PROFILE_FOLLOW_URL, self.author, FOUND],
            [PROFILE_UNFOLLOW_URL, self.guest, FOUND],
            [PROFILE_UNFOLLOW_URL, self.another, FOUND],
            [PROFILE_UNFOLLOW_URL, self.author, NOT_FOUND],
        ]
        for url, client, expect in cases:
            with self.subTest(url=url, client=client, expect=expect):
                self.assertEqual(
                    client.get(url).status_code,
                    expect
                )

    def test_pages_url_redirect(self):
        """Проверка перенаправлений"""
        url_names = [
            [POST_CREATE_URL, self.guest, REDIRECTS_POST_CREATE_URL],
            [self.POST_EDIT_URL, self.guest, self.REDIRECTS_POST_EDIT_URL],
            [PROFILE_FOLLOW_URL, self.guest, REDIRECTS_PROFILE_FOLLOW_URL],
            [PROFILE_UNFOLLOW_URL, self.guest, REDIRECTS_PROFILE_UNFOLLOW_URL],
            [PROFILE_FOLLOW_URL, self.another, PROFILE_URL],
            [PROFILE_UNFOLLOW_URL, self.another, PROFILE_URL],
            [PROFILE_FOLLOW_URL, self.author, PROFILE_URL],
            [self.POST_EDIT_URL, self.another, PROFILE_AUTH_URL],
        ]
        for url, user, redirect in url_names:
            with self.subTest(url=url, user=user, redirect=redirect):
                self.assertRedirects(
                    user.get(url, follow=True),
                    redirect
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            FOLLOW_INDEX_URL: 'posts/follow.html',
            GROUP_LIST_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            POST_CREATE_URL: 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.author.get(address),
                    template
                )

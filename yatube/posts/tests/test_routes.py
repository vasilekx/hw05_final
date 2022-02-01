# posts/tests/test_routes.py

from django.test import TestCase
from django.urls import reverse

from ..urls import app_name

USERNAME = 'test_user'
GROUP_SLUG = 'test-slug'
POST_ID = 1


class PostsRoutesTests(TestCase):
    def test_urls_routes(self):
        """Проверка маршрутов"""
        templates_url_names = [
            ['/', 'index', None],
            ['/follow/', 'follow_index', None],
            ['/create/', 'post_create', None],
            [f'/group/{GROUP_SLUG}/', 'group_list', [GROUP_SLUG]],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
            [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
            [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
            [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
            [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
        ]
        for url, route, arg in templates_url_names:
            with self.subTest(url=url, route=route, arg=arg):
                self.assertEqual(
                    url,
                    reverse(f'{app_name}:{route}', args=arg)
                )

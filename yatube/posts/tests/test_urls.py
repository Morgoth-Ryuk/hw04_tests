from django.test import TestCase, Client
from ..models import User, Post, Group
from django.urls import reverse
from http import HTTPStatus


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост_123456',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_url_exists_at_desired_location_unauthorized_client(self):
        """Страницы доступные любому пользователю."""
        url_names = {
            reverse('posts:index'): HTTPStatus.OK.value,
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): HTTPStatus.OK.value,
            reverse(
                'posts:profile', kwargs={'username': self.author}
            ): HTTPStatus.OK.value,
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK.value,
            '/notexist_page/': HTTPStatus.NOT_FOUND.value,
        }
        for adress, code in url_names.items():
            with self.subTest(code=code):
                self.assertEqual(
                    self.guest_client.get(adress).status_code, code
                )

    def test_url_exists_at_desired_location_authorized_client(self):
        """Страницы доступные авторизованному пользователю."""
        if self.author:
            self.assertEqual(
                self.author_client.get(
                    reverse(
                        'posts:post_edit', kwargs={'post_id': self.post.id}
                    )
                ).status_code, HTTPStatus.OK.value
            )
        self.assertEqual(
            self.authorized_client.get(
                reverse('posts:post_create')
            ).status_code, HTTPStatus.OK.value
        )

    def test_posts_urls_redirect_anonymous_client(self):
        """Перенаправление анонимного пользователя."""
        urls_names = {
            reverse('posts:post_create'): reverse(
                'users:login'
            ) + '?next=' + reverse('posts:post_create'),
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): reverse('users:login') + '?next=' + reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            )
        }
        for adress, redirect in urls_names.items():
            with self.subTest(adress=adress):
                self.assertRedirects(
                    self.guest_client.get(adress, follow=True), redirect
                )

    def test_posts_urls_redirect_authorized_client(self):
        """Перенаправление авторизованного пользователя."""
        self.assertRedirects(
            self.authorized_client.get(
                reverse(
                    'posts:post_edit', kwargs={'post_id': self.post.id}
                ), follow=True),
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )

    def test_posts_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.author}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        if self.author:
            self.assertTemplateUsed(
                self.author_client.get(reverse(
                    'posts:post_edit', kwargs={'post_id': self.post.id}
                )),
                'posts/create_post.html'
            )
        for adress, template in url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(
                    self.authorized_client.get(adress), template
                )

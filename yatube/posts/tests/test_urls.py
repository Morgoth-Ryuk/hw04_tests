from django.test import TestCase, Client
from ..models import User, Post, Group


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
            '/': 200,
            f'/group/{self.post.group.slug}/': 200,
            f'/profile/{self.post.author.username}/': 200,
            f'/posts/{self.post.id}/': 200,
            '/notexist_page/': 404,
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
                    f'/posts/{self.post.id}/edit/').status_code,
                200
            )
        self.assertEqual(
            self.authorized_client.get('/create/').status_code,
            200
        )

    def test_posts_urls_redirect_anonymous_client(self):
        """Перенаправление анонимного пользователя."""
        urls_names = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/': (
                f'/auth/login/?next=/posts/{self.post.id}/edit/')
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
                f'/posts/{self.post.id}/edit/', follow=True),
            f'/posts/{self.post.id}/'
        )

    def test_posts_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        if self.author:
            self.assertTemplateUsed(
                self.author_client.get(f'/posts/{self.post.id}/edit/'),
                'posts/create_post.html'
            )
        for adress, template in url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(
                    self.authorized_client.get(adress), template
                )

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from ..models import User, Post, Group

User = get_user_model()


class ViewPostsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост_123456',
            author=cls.author,
            group=cls.group,
        )
        cls.user = User.objects.create_user(username='Test')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
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
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_group_detail_pages_show_correct_context(self):
        """Шаблоны index, group_list, post_detail """
        """сформированы с правильным контекстом."""
        pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ),
        }
        for value, expected in pages.items():
            with self.subTest(value=value):
                here_template = pages[value]
                response = self.authorized_client.get(here_template)
                self.assertEqual(
                    response.context.get('post').text, self.post.text)
                self.assertEqual(
                    response.context.get('post').group, self.post.group)
                self.assertEqual(
                    response.context.get('post').author, self.post.author)
                self.assertEqual(
                    response.context.get('post').pub_date, self.post.pub_date)

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.post.author}
        ))
        self.assertEqual(
            response.context.get('post_list')[0].text, self.post.text)
        self.assertEqual(
            response.context.get('post_list')[0].group, self.post.group)
        self.assertEqual(
            response.context.get('post_list')[0].author, self.post.author)
        self.assertEqual(
            response.context.get('post_list')[0].pub_date, self.post.pub_date)

    def test_create_post_pages_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_pages_show_correct_on_pages(self):
        """Проверка появляется ли пост на страницах с выбранной группой"""
        form_fields = {
            reverse('posts:index'): Post.objects.get(group=self.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.group),
            reverse(
                'posts:profile', kwargs={'username': self.author}
            ): Post.objects.get(group=self.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)

    class PaginatorViewsTest(TestCase):
        POSTS_NUMBER = 10
        REST_POSTS = 3

        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            cls.author = User.objects.create_user(username="auth")
            cls.group = Group.objects.create(
                title='Тестовая группа',
                slug='test_slug',
                description='Тестовое описание',
            )
            posts_list = [
                Post(
                    author=cls.author,
                    text=f'Тестовый пост {count}',
                    group=cls.group,
                )
                for count in range(13)
            ]
            Post.objects.bulk_create(posts_list)

        def setUp(self):
            self.author_client = Client()
            self.author_client.force_login(self.author)
            self.post = Post.objects.get(id=1)

        def test_paginator_count_posts(self):
            reverse_values = (
                reverse('posts:index'),
                reverse('posts:group_list', kwargs={'slug': self.group.slug}),
                reverse('posts:profile', kwargs={'username': self.author}),
            )
            for reverse_value in reverse_values:
                with self.subTest(reverse_value=reverse_value):
                    response = self.author_client.get(reverse_value)
                    self.assertEqual(
                        len(response.context.get('page_obj').object_list),
                        self.POSTS_NUMBER
                    )
                    response = self.author_client.get(
                        reverse_value + '?page=2'
                    )
                    self.assertEqual(
                        len(response.context.get('page_obj').object_list),
                        self.REST_POSTS
                    )

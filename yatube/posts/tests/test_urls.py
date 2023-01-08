from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from http import HTTPStatus
from django.urls import reverse

User = get_user_model()


class PostsURLTEST(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.quest_user = Client()
        cls.user = User.objects.create_user(username='NoName')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.status_code_quest = {
            '/': HTTPStatus.OK,
            '/group/test_slug/': HTTPStatus.OK,
            '/profile/NoName/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        cls.urls_template = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
            '/follow/': 'posts/follow.html'
        }

    def test_urls_status_code_quest_user(self):
        """Проверка доступности страниц для гостя"""
        for url, status_code in self.status_code_quest.items():
            with self.subTest(url=url):
                response = self.quest_user.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_status_code_authorized_user(self):
        """Проверка доступности страницы создания поста
        для авторизованного юзера"""
        self.assertEqual(self.authorized_user.get(
            '/create/').status_code, HTTPStatus.OK)

    def test_urls_correct_templates(self):
        """Проверка соответствия шаблонов к URL-адресам"""
        for url, template_name in self.urls_template.items():
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertTemplateUsed(response, template_name)

    def test_url_edit_redirect(self):
        """Проверка редиректа для гостя при переходе на редактирование поста"""
        response = self.quest_user.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_url_edit_redirect(self):
        """Проверка редиректа для гостя при переходе на создание комментария"""
        response = self.quest_user.get('/posts/1/comment/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')

    def test_tamplate_author(self):
        """Проверка вызова шаблона при редактировании поста автором"""
        response = self.authorized_user.get('/posts/1/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_redirect_quest_user_edit_post(self):
        """Проверка редиректа залогиненного юзера, но не автора
        при переходе на редактирование поста"""
        user_no_author = User.objects.create_user(username='NoNameNoAuthor')
        authorized_user_no_author = Client()
        authorized_user_no_author.force_login(user_no_author)
        response_no_author = authorized_user_no_author.get(
            '/posts/1/edit/', follow=True)
        self.assertRedirects(response_no_author, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))

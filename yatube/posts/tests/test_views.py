from django.core.cache import cache
import shutil
from posts.tests.test_forms import SMALL_GIF, TEMP_MEDIA_ROOT
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Follow

User = get_user_model()
TEST_POST = 12
OBJ_IN_FIRST_PAGE = 10


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.view_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}): (
                'posts/group_list.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
        }

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_correct_template(self):
        """Проверка корректности шаблонов."""
        for view, template in self.view_templates.items():
            with self.subTest(view=view):
                response = self.authorized_user.get(view)
                self.assertTemplateUsed(response, template)

    def test_context_template_index(self):
        """Проверка ожидаемого контекста в шаблоне index"""
        response = self.authorized_user.get(reverse('posts:index'))
        expected = list(Post.objects.all()[:OBJ_IN_FIRST_PAGE])
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_context_template_group_list(self):
        """Проверка ожидаемого контекста в шаблоне group_list"""
        response = self.authorized_user.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        expected = list(Post.objects.filter(
            group_id=self.group.id)[:OBJ_IN_FIRST_PAGE])
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_context_template_profile(self):
        """Проверка ожидаемого контекста в шаблоне profile"""
        response = self.authorized_user.get(reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        expected = list(Post.objects.filter(
            author_id=self.user.id)[:OBJ_IN_FIRST_PAGE])
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_context_template_post_detail(self):
        """Проверка ожидаемого контекста в шаблоне post_detail"""
        response = self.authorized_user.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        objfields_expectedfields = {
            response.context.get('post').text: self.post.text,
            response.context.get('post').author: self.post.author,
            response.context.get('post').group: self.post.group,
            response.context.get('post').image: 'posts/small.gif',
        }
        for objfield, expfield in objfields_expectedfields.items():
            with self.subTest(objfield=objfield):
                self.assertEqual(objfield, expfield)

    def test_form_create_and_edit(self):
        """Проверка контекста создания и редактирования поста"""
        responses = [
            self.authorized_user.get(reverse('posts:post_create')),
            self.authorized_user.get(reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}))]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for response in responses:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_create_post_show_in_index_group_profile(self):
        """Проверка появления поста на нужных страницах при его создании"""
        post_new = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=self.uploaded,
        )
        responses = [
            self.authorized_user.get(reverse('posts:index')),
            self.authorized_user.get(
                reverse('posts:group_list', kwargs={'slug': self.group.slug}))]
        for response in responses:
            self.assertIn(post_new, response.context['page_obj'])

    def test_correct_groups(self):
        """Проверка, что при создании поста с другой группой
        он не попадает в группу, для которой не был предназначен"""
        group_new = Group.objects.create(
            title='Тестовый заголовок_new',
            slug='test_slug2',
            description='Тестовое описание группы_new',
        )
        post_new = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=group_new,
            image=self.uploaded,
        )
        response_old_group = self.authorized_user.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        old_group_obj = response_old_group.context['page_obj']
        response_new_group = self.authorized_user.get(
            reverse('posts:group_list', kwargs={'slug': group_new.slug}))
        new_group_obj = response_new_group.context['page_obj']
        self.assertNotIn(post_new, old_group_obj)
        self.assertIn(post_new, new_group_obj)

    def test_follow_unfollow(self):
        """Проверка работы подписок и отписок"""
        User.objects.create_user(username='NoName_NEW')
        self.authorized_user.get(
            reverse('posts:profile_follow', kwargs={'username': 'NoName_NEW'})
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.authorized_user.get(
            reverse('posts:profile_unfollow', kwargs={
                'username': 'NoName_NEW'})
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_index_follow_unfollow(self):
        """Проверка отображения главной страницы с подпиской на авторов"""
        user_new = User.objects.create_user(username='NoName_NEW')
        authorized_user_new = Client()
        authorized_user_new.force_login(user_new)
        post_user_new = Post.objects.create(
            text='Тестовый текст New',
            author=user_new,
            group=self.group,
        )
        self.authorized_user.get(
            reverse('posts:profile_follow', kwargs={'username': 'NoName_NEW'})
        )
        response = self.authorized_user.get(reverse('posts:follow_index'))
        self.assertIn(post_user_new, response.context['page_obj'])
        response = authorized_user_new.get(reverse('posts:follow_index'))
        self.assertNotIn(post_user_new, response.context['page_obj'])

    def test_cache_work(self):
        """Проверка работы кэша"""
        post_cache = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=self.uploaded,
        )
        response_before_del = self.authorized_user.get(reverse('posts:index'))
        cache_before_delete = response_before_del.content
        post_cache.delete()
        response_after_del = self.authorized_user.get(reverse('posts:index'))
        cache_after_delete = response_after_del.content
        self.assertEqual(cache_before_delete, cache_after_delete)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        for post in range(TEST_POST):
            Post.objects.create(
                text='Тест для пагинатора',
                author=cls.user,
                group=cls.group,)
        cls.urls = {reverse('posts:index'): OBJ_IN_FIRST_PAGE,
                    reverse('posts:group_list', kwargs={
                        'slug': 'test_slug'}): OBJ_IN_FIRST_PAGE,
                    reverse('posts:profile', kwargs={
                        'username': 'NoName'}): OBJ_IN_FIRST_PAGE}

    def setUp(self):
        cache.clear()

    def test_paginators_first_page(self):
        """ Проверка пагинатора для первой страницы."""
        for url, obj in self.urls.items():
            with self.subTest(url=url):
                response = self.authorized_user.get(url)
                self.assertEqual(len(response.context['page_obj']), obj)

    def test_paginators_second_page(self):
        """ Проверка пагинатора для второй страницы."""
        for url in self.urls:
            OBJ_IN_SECOND_PAGE = 3
            response = self.authorized_user.get(url + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), OBJ_IN_SECOND_PAGE)

from http import HTTPStatus
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание группы',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Валидная форма создает запись в Posts."""
        form_data = {
            'text': 'Другой текст',
            'group': self.group.id,
            'author': self.user,
            'image': self.uploaded,
        }
        post_create = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(post_create.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.last()
        fields_texts = {
            post.text: 'Другой текст',
            post.author: self.user,
            post.group: self.group,
            post.image: 'posts/small.gif',
        }
        for field, text in fields_texts.items():
            with self.subTest(field=field):
                self.assertEqual(field, text)

    def test_edit_post(self):
        """Валидная форма редактирует запись."""
        group_new = Group.objects.create(
            title='Тестовый заголовок_new',
            slug='test_slug_new',
            description='Тестовое описание группы_new',
        )
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': 'Изменил текст',
            'group': group_new.id,
            'author': self.user,
            'image': self.uploaded,
        }
        post_edit = self.authorized_user.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(post_edit.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), 1)
        post_new = Post.objects.last()
        fields_texts = {
            post_new.text: 'Изменил текст',
            post_new.author: self.user,
            post_new.group: group_new,
        }
        for field, text in fields_texts.items():
            with self.subTest(field=field):
                self.assertEqual(field, text)
        self.assertEqual(self.group.posts.count(), 0)

    def test_create_comment(self):
        """Валидная форма создает комментарий."""
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': 'Комментарий',
            'author': self.user,
        }
        comment_create = self.authorized_user.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(comment_create.status_code, HTTPStatus.OK)
        self.assertEqual(post.comments.count(), 1)
        comment = post.comments.last()
        fields_texts = {
            comment.text: 'Комментарий',
            post.author: self.user,
        }
        for field, text in fields_texts.items():
            with self.subTest(field=field):
                self.assertEqual(field, text)

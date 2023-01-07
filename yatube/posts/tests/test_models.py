from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, TEXT_LIMIT

User = get_user_model()
TEST_TEXT_UPDATE = 3
VERBOSE_NAME_POST_OBJ = 'Пост'
VERBOSE_NAME_PLURAL_POST_OBJ = 'Посты'
VERBOSE_NAME_GROUP_OBJ = 'Группа'
VERBOSE_NAME_PLURAL_GROUP_OBJ = 'Группы'
VERBOSE_NAME_COMMENT_OBJ = 'Комментарий'
VERBOSE_NAME_PLURAL_COMMENT_OBJ = 'Комментарии'
VERBOSE_NAME_TEXT = 'Введите текст'
VERBOSE_NAME_GROUP = 'Выберите группу'
VERBOSE_NAME_PUB_DATE = 'Дата создания'
VERBOSE_NAME_IMAGE = 'Картинка'
VERBOSE_NAME_COMMENT_TEXT = 'Добавить комментарий:'
VERBOSE_NAME_COMMENT_POST = 'Пост'
VERBOSE_NAME_COMMENT_AUTHOR = 'Автор'
VERBOSE_NAME_COMMENT_CREATED = 'Дата создания'
HELP_TEXT_TEXT = 'Текст нового поста'
HELP_TEXT_GROUP = 'Группа, к которой будет относиться пост'
HELP_TEXT_IMAGE = 'Ваша картинка'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * TEST_TEXT_UPDATE,
        )
        cls.comment = Comment.objects.create(
            text='Комментарий',
            author=cls.user,
            post=cls.post,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__.
        И что усечение __str__ для модели Post работает правильно."""
        strsmodels_texts = {
            self.post: self.post.text[:TEXT_LIMIT],
            self.group: self.group.title,
            self.comment: self.comment.text[:TEXT_LIMIT],
        }
        for strmodel, text in strsmodels_texts.items():
            with self.subTest(strmodel=strmodel):
                self.assertEqual(str(strmodel), text)

    def test_verbose_name(self):
        """Проверяем, что verbose_name модели Post совпадает с ожидаемым."""
        get_verboses_verbose = {
            self.post._meta.get_field('text').verbose_name: VERBOSE_NAME_TEXT,
            self.post._meta.get_field(
                'group').verbose_name: VERBOSE_NAME_GROUP,
            self.post._meta.get_field(
                'pub_date').verbose_name: VERBOSE_NAME_PUB_DATE,
            self.post._meta.get_field(
                'image').verbose_name: VERBOSE_NAME_IMAGE,
            self.post._meta.verbose_name: VERBOSE_NAME_POST_OBJ,
            self.post._meta.verbose_name_plural: VERBOSE_NAME_PLURAL_POST_OBJ,
        }
        for get_verbose, verbose in get_verboses_verbose.items():
            with self.subTest(verbose=verbose):
                self.assertEqual(get_verbose, verbose)

    def test_help_text(self):
        """Проверяем, что help_text модели Post совпадает с ожидаемым."""
        get_help_text_verbose = {
            self.post._meta.get_field('text').help_text: HELP_TEXT_TEXT,
            self.post._meta.get_field('group').help_text: HELP_TEXT_GROUP,
            self.post._meta.get_field(
                'image').help_text: HELP_TEXT_IMAGE,
        }
        for get_help_text, verbose in get_help_text_verbose.items():
            with self.subTest(verbose=verbose):
                self.assertEqual(get_help_text, verbose)

    def test_verbose_name(self):
        """Проверяем, что verbose_name модели Group совпадает с ожидаемым."""
        get_verboses_verbose = {
            self.group._meta.verbose_name: VERBOSE_NAME_GROUP_OBJ,
            self.group._meta.verbose_name_plural:
                VERBOSE_NAME_PLURAL_GROUP_OBJ,
        }
        for get_verbose, verbose in get_verboses_verbose.items():
            with self.subTest(verbose=verbose):
                self.assertEqual(get_verbose, verbose)

    def test_verbose_name(self):
        """Проверяем, что verbose_name модели Comment совпадает с ожидаемым."""
        get_verboses_verbose = {
            self.comment._meta.get_field(
                'post').verbose_name: VERBOSE_NAME_COMMENT_POST,
            self.comment._meta.get_field(
                'author').verbose_name: VERBOSE_NAME_COMMENT_AUTHOR,
            self.comment._meta.get_field(
                'text').verbose_name: VERBOSE_NAME_COMMENT_TEXT,
            self.comment._meta.get_field(
                'pub_date').verbose_name: VERBOSE_NAME_COMMENT_CREATED,
            self.comment._meta.verbose_name: VERBOSE_NAME_COMMENT_OBJ,
            self.comment._meta.verbose_name_plural:
                VERBOSE_NAME_PLURAL_COMMENT_OBJ,
        }
        for get_verbose, verbose in get_verboses_verbose.items():
            with self.subTest(verbose=verbose):
                self.assertEqual(get_verbose, verbose)

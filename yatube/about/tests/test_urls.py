from django.test import TestCase, Client
from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адресов /about/author/ и /about/tech/."""
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.guest_client.get(
                    url).status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        for url, template in self.urls.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(self.guest_client.get(url), template)

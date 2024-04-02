from django.test import TestCase, Client
from django.urls import reverse


class StaticURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_author_page_status(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech_page_status(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_about_uses_correct_template(self):
        templates_url_names = {
            'about/author.html': reverse("about:author"),
            'about/tech.html': reverse("about:tech"),
        }

        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
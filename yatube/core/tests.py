from django.test import TestCase


# Create your tests here.
class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        template = 'core/404.html'
        self.assertTemplateUsed(response, template)
from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    url_names = {
        'about/author.html': '/about/author/',
        'about/tech.html': '/about/tech/',
    }

    def test_about_page_accessible_by_name_all(self):
        """URL, генерируемый при помощи имени about:author, доступен."""
        response_author = self.guest_client.get(reverse('about:author'))
        response_tech = self.guest_client.get(reverse('about:tech'))
        respons_and_urls = {
            '/about/author/': response_tech.status_code,
            '/about/tech/': response_author.status_code,
        }
        for adress, code in respons_and_urls.items():
            with self.subTest(code=code):
                self.assertEqual(
                    self.guest_client.get(adress).status_code, code
                )

    def test_about_page_uses_correct_template_all(self):
        """URL, генерируемый при помощи имени about:author, доступен."""
        templates_and_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for adress, template in templates_and_urls.items():
            with self.subTest(template=template):
                self.assertTemplateUsed(
                    self.guest_client.get(adress), template)

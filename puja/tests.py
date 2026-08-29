from django.test import TestCase
from django.urls import reverse
from puja.models import CustomUser

class PujaPortalTests(TestCase):
    def test_anonymous_redirect_to_login(self):
        """Anonymous users must be redirected to the login page when visiting dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_login_page_renders(self):
        """Login page should load correctly."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'puja/login.html')


from django.test import TestCase
from django.urls import reverse
from puja.models import CustomUser

class PujaPortalTests(TestCase):
    def test_anonymous_dashboard_access(self):
        """Anonymous users should be able to view the dashboard directly."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirect_to_login_on_write(self):
        """Anonymous users must be redirected to the login page when visiting add donation."""
        response = self.client.get(reverse('donation_add'))
        self.assertEqual(response.status_code, 302)

    def test_login_page_renders(self):
        """Login page should load correctly."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'puja/login.html')


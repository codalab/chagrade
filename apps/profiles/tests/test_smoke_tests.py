from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class ProfilesSmokeTests(TestCase):

    def test_profiles_login_works(self):
        resp = self.client.get(reverse('profiles:login'))
        assert resp.status_code == 200

    def test_profiles_change_passwords_view_works(self):
        # Trying to change password not logged in should force login
        resp = self.client.get(reverse('profiles:change_password'))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Login and attempt to view change password page
        User.objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('profiles:change_password'))
        assert resp.status_code == 200

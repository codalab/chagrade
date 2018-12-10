from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.klasses.models import Klass
from apps.profiles.models import Instructor
from apps.homework.models import Submission
from apps.profiles.models import ChaUser, StudentMembership


User = get_user_model()


class ProfilesSmokeTests(TestCase):

    def setUp(self):
        User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")

    def test_profiles_login_returns_200(self):
        resp = self.client.get(reverse('profiles:login'))
        assert resp.status_code == 200

    def test_profiles_change_passwords_view_returns_200(self):
        # Trying to change password not logged in should force login
        resp = self.client.get(reverse('profiles:change_password'))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Login and attempt to view change password page
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('profiles:change_password'))
        assert resp.status_code == 200

    def test_instructor_signup_returns_200(self):
        # check that an instructor can reach the sign-in page
        resp = self.client.get(reverse('profiles:instructor_signup'))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to sign-in as instructor
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('profiles:instructor_signup'))
        assert resp.status_code == 200

    def test_instructor_overview_returns_200(self):
        # check that the instructor is signed in
        resp = self.client.get(reverse('profiles:instructor_overview'))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to see a users profile
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('profiles:instructor_signup'))
        assert resp.status_code == 200

    def test_student_overview_returns_200(self):
        # check that the student is signed in
        resp = self.client.get(reverse('profiles:student_overview'))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to see the overview for students
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('profiles:student_overview'))
        assert resp.status_code == 200

    def test_my_profile_returns_200(self):
        # check that the user is signed in
        resp = self.client.get(reverse('profiles:my_profile'))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to see the overview for instructors
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('profiles:my_profile'))
        assert resp.status_code == 200

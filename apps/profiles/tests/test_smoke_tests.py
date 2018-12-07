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

    def test_create_klass_returns_200(self):
        # Trying not logged in to create klass
        resp = self.client.get(reverse('klasses:create_klass'))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to create klass
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('klasses:create_klass'))
        assert resp.status_code == 200

    def test_edit_klass_returns_200(self):
        # Trying not logged in to edit klass
        resp = self.client.get(reverse('klasses:edit_klass', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to edit klass as instructor
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('klasses:edit_klass', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

    def test_klass_details_returns_200(self):
        # Trying not logged in to view klass overview
        resp = self.client.get(reverse('klasses:klass_details', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to view klass overview
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('klasses:klass_details', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

    def test_klass_enrollment_returns_200(self):
        # Trying not logged in to view klass enrollment
        resp = self.client.get(reverse('klasses:klass_enrollment', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to view klass enrollment
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('klasses:klass_enrollment', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

    def test_klass_homework_view_returns_200(self):
        # Trying not logged in to view klass homework
        resp = self.client.get(reverse('klasses:klass_homework', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to view klass homework
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('klasses:klass_homework', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

    def test_klass_grading_homework_view_returns_200(self):
        # Trying not logged in to view how badly you failed that klass, man
        resp = self.client.get(reverse('klasses:klass_grading', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to view how badly you failed that klass, bro
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('klasses:klass_grading', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

    def test_klass_activate_view_returns_200(self):
        # Trying not logged in to view klass homework
        resp = self.client.get(reverse('klasses:klass_activate', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to view klass homework
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('klasses:klass_activate', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

    def test_homework_define_homework_returns_200(self):
        # Trying not logged in to edit klass
        resp = self.client.get(reverse('homework:define_homework', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to edit klass as instructor
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('homework:define_homework', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

    def test_homework_grade_homework_view_returns_200(self):
        #  creating the instructor, klass, a fake student, and submission objects for the test
        faker = ChaUser.objects.create()
        fakestudent = StudentMembership.objects.create(user=faker, klass=self.klass, student_id=1)
        submission = Submission.objects.create(klass=self.klass, creator=fakestudent)

        # Trying not logged in to edit klass
        resp = self.client.get(reverse('homework:grade_homework',
                                       kwargs={'klass_pk': self.klass.pk, 'submission_pk': submission.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to edit klass as instructor
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('homework:grade_homework',
                                       kwargs={'klass_pk': self.klass.pk, 'submission_pk': submission.pk}))
        assert resp.status_code == 200

    def test_homework_submit_homework_view_returns_200(self):
        # Trying not logged in to edit klass
        resp = self.client.get(reverse('homework:submit_homework', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 302
        assert resp.url.startswith(reverse('profiles:login'))

        # Trying while logged in to edit klass as instructor
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('homework:submit_homework', kwargs={'klass_pk': self.klass.pk}))
        assert resp.status_code == 200

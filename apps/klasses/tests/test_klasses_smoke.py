from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.klasses.models import Klass
from apps.profiles.models import Instructor
from apps.homework.models import Submission
from apps.profiles.models import ChaUser, StudentMembership


User = get_user_model()


class KlassesSmokeTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create()
        self.user.instructor = self.instructor
        self.user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")

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

    # TODO: Re-write test for needed definition
    # def test_homework_grade_homework_view_returns_200(self):
    #     #  creating the instructor, klass, a fake student, and submission objects for the test
    #     faker = ChaUser.objects.create()
    #     fakestudent = StudentMembership.objects.create(user=faker, klass=self.klass, student_id=1)
    #     submission = Submission.objects.create(klass=self.klass, creator=fakestudent)
    #
    #     # Trying not logged in to edit klass
    #     resp = self.client.get(reverse('homework:grade_homework',
    #                                    kwargs={'klass_pk': self.klass.pk, 'submission_pk': submission.pk}))
    #     assert resp.status_code == 302
    #     assert resp.url.startswith(reverse('profiles:login'))
    #
    #     # Trying while logged in to edit klass as instructor
    #     self.client.login(username='user', password='pass')
    #     resp = self.client.get(reverse('homework:grade_homework',
    #                                    kwargs={'klass_pk': self.klass.pk, 'submission_pk': submission.pk}))
    #     assert resp.status_code == 200

    # TODO: Re-write test for new URL: Needs a definition PK
    # def test_homework_submit_homework_view_returns_200(self):
    #     # Trying not logged in to edit klass
    #     resp = self.client.get(reverse('homework:submit_homework', kwargs={'klass_pk': self.klass.pk}))
    #     assert resp.status_code == 302
    #     assert resp.url.startswith(reverse('profiles:login'))
    #
    #     # Trying while logged in to edit klass as instructor
    #     self.client.login(username='user', password='pass')
    #     resp = self.client.get(reverse('homework:submit_homework', kwargs={'klass_pk': self.klass.pk}))
    #     assert resp.status_code == 200

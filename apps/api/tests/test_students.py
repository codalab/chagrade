from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.homework.models import Submission, Definition
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership

User = get_user_model()


class StudentsAPIEndpointTests(TestCase):

    def setUp(self):
        self.student_user = User.objects.create_user(
            username='student_user',
            password='pass'
        )
        self.instructor = Instructor.objects.create(
            university_name='Test'
        )
        self.klass = Klass.objects.create(
            instructor=self.instructor,
            course_number="1"
        )
        self.student = StudentMembership.objects.create(
            user=self.student_user,
            klass=self.klass,
            student_id='test_id'
        )
        self.main_user = User.objects.create_user(
            username='user',
            password='pass'
        )
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor

    def test_anonymous_permissions(self):
        resp = self.client.get(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.get(path=reverse(
            'api:studentmembership-detail',
            kwargs={'version': 'v1', 'pk': self.student.pk}))
        assert resp.status_code == 401

    def test_authenticated_permissions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(path=reverse(
            'api:studentmembership-detail',
            kwargs={'version': 'v1', 'pk': self.student.pk}))
        assert resp.status_code == 200

    def test_instructor_permissions(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(path=reverse(
            'api:studentmembership-detail',
            kwargs={'version': 'v1', 'pk': self.student.pk}))
        assert resp.status_code == 200




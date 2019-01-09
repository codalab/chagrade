from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.homework.models import Definition, Criteria
from apps.klasses.models import Klass
from apps.profiles.models import Instructor

User = get_user_model()


class CriteriaGETMethodTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(
            username='user',
            password='pass')
        self.instructor = Instructor.objects.create(
            university_name='Test'
        )
        self.main_user.instructor = self.instructor
        self.student_user = User.objects.create_user(
            username='student_user',
            password='pass'
        )
        self.main_user.save()
        self.klass = Klass.objects.create(
            instructor=self.instructor,
            course_number="1"
        )
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='test',
            description='test'
        )
        self.criteria = Criteria.objects.create(
            definition=self.definition,
            description='Test Criteria',
            lower_range=0,
            upper_range=10
        )

    def test_anonymous_user_cannot_get_criterias(self):
        resp = self.client.get(path=reverse(
            'api:criteria-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.get(path=reverse(
            'api:criteria-detail',
            kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.status_code == 401

    def test_student_user_can_get_criterias(self):
        self.client.login(username='student_user', password='pass')

        resp = self.client.get(path=reverse(
            'api:criteria-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(path=reverse(
            'api:criteria-detail',
            kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.json()['description'] == 'Test Criteria'

    def test_instructor_user_can_get_criterias(self):
        self.client.login(username='user', password='pass')

        resp = self.client.get(path=reverse(
            'api:criteria-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(path=reverse(
            'api:criteria-detail',
            kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.json()['description'] == 'Test Criteria'

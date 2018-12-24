from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from apps.homework.models import Definition
from apps.klasses.models import Klass
from apps.profiles.models import Instructor

User = get_user_model()


class DefinitionAPIEndpointsTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.main_user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='test',
            description='test')

    def test_anonymous_permissions(self):
        resp = self.client.get(path=reverse(
            'api:definition-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(path=reverse(
            'api:definition-list',
            kwargs={'version': 'v1'}),
            data={'klass': self.klass.pk,
                  'creator': self.instructor.pk,
                  'due_date': timezone.now(),
                  'name': 'test',
                  'description': 'test'})
        assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:definition-detail',
            kwargs={'version': 'v1', 'pk': self.definition.pk}),
            data={'name': 'A Different Name'},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(reverse(
            'api:definition-detail',
            kwargs={'version': 'v1', 'pk': self.definition.pk}))
        assert resp.status_code == 401

    def test_authenticated_permissions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:definition-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:definition-list',
            kwargs={'version': 'v1'}),
            data={'klass': self.klass.pk,
                  'creator': self.instructor.pk,
                  'due_date': timezone.now(),
                  'name': 'test1',
                  'description': 'test'})
        assert resp.status_code == 201
        assert resp.json()['name'] == 'test1'

        resp = self.client.put(path=reverse(
            'api:definition-detail',
            kwargs={'version': 'v1', 'pk': '2'}),
            data={'name': 'A Different Name',
                  'klass': self.klass.pk,
                  'creator': self.instructor.pk},
            content_type='application/json')
        assert resp.status_code == 403

        resp = self.client.delete(path=reverse(
            'api:definition-detail',
            kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 403

    def test_instructor_permissions(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:definition-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:definition-list',
            kwargs={'version': 'v1'}),
            data={'klass': self.klass.pk,
                  'creator': self.instructor.pk,
                  'due_date': timezone.now(),
                  'name': 'test_definition',
                  'description': 'test'})
        data = resp.json()
        assert data['name'] == 'test_definition'
        assert resp.status_code == 201

        resp = self.client.put(path=reverse(
            'api:definition-detail',
            kwargs={'version': 'v1', 'pk': '2'}),
            data={'name': 'A Different Name',
                  'klass': self.klass.pk,
                  'creator': self.instructor.pk},
            content_type='application/json')
        data = resp.json()
        assert data['name'] == 'A Different Name'
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse(
            'api:definition-detail',
            kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204


from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership

User = get_user_model()


class KlassesAPIEndpointTests(TestCase):

    def setUp(self):
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.klass = Klass.objects.create(
            instructor=self.instructor,
            course_number="1")
        self.student = StudentMembership.objects.create(
            user=self.student_user,
            klass=self.klass,
            student_id='test_id')
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.main_user.set_password('pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()

    def test_anonymous_permissions(self):
        resp = self.client.get(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1'}),
            data={'title': 'Test', 'instructor': self.instructor.pk})
        assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:klass-detail',
            kwargs={'version': 'v1', 'pk': self.klass.pk}),
            data={'title': 'A Different Name'},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse(
            'api:klass-detail',
            kwargs={'version': 'v1', 'pk': self.klass.pk}))
        assert resp.status_code == 401

    def test_authenticated_permissions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1'}),
            data={'title': 'Test',
                  'instructor': self.instructor.pk,
                  'course_number': 2})
        # TODO: Block this
        # assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1', 'pk': self.klass.pk}),
            data={'title': 'A Different Name',
                  'instructor': self.instructor.pk,
                  'course_number': 1},
            content_type='application/json')
        assert resp.status_code == 403

        resp = self.client.delete(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1', 'pk': self.klass.pk}))
        assert resp.status_code == 403

    def test_instructor_permissions(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:klass-list',
            kwargs={'version': 'v1'}),
            data={'title': 'Test',
                  'instructor': self.instructor.pk,
                  'course_number': 2})
        data = resp.json()
        assert resp.status_code == 201
        assert data['title'] == 'Test'

        resp = self.client.put(path=reverse(
            'api:klass-detail',
            kwargs={'version': 'v1', 'pk': '2'}),
            data={'title': 'A Different Name',
                  'instructor': self.instructor.pk,
                  'course_number': 2},
            content_type='application/json')
        data = resp.json()
        assert resp.status_code == 200
        assert data['title'] == "A Different Name"

        resp = self.client.delete(path=reverse(
            'api:klass-detail',
            kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

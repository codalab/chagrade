from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.profiles.models import Instructor

User = get_user_model()

class UsersAPIEndpointsTests(TestCase):

    def setUp(self):
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.main_user.set_password('pass')
        self.main_user.save()
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()

    def test_anonymous_permissions(self):
        resp = self.client.get(path=reverse(
            'api:chauser-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(path=reverse(
            'api:chauser-list',
            kwargs={'version': 'v1'}),
            data={'username': 'new_user'})
        assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:chauser-detail',
            kwargs={'version': 'v1', 'pk': self.student_user.pk}),
            data={'username': 'new_user'},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse(
            'api:chauser-detail',
            kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 401

    def test_student_permissions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:chauser-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:chauser-list',
            kwargs={'version': 'v1'}),
            data={'username': 'new_user'})
        assert resp.status_code == 405

        resp = self.client.put(path=reverse(
            'api:chauser-detail',
            kwargs={'version': 'v1', 'pk': self.student_user.pk}),
            data={'username': 'new_user'})
        assert resp.status_code == 405

        resp = self.client.delete(path=reverse(
            'api:chauser-detail',
            kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 405

    def test_instructor_permissions(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:chauser-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:chauser-list',
            kwargs={'version': 'v1'}),
            data={'username': 'new_user'})
        assert resp.status_code == 405

        resp = self.client.put(path=reverse(
            'api:chauser-detail',
            kwargs={'version': 'v1', 'pk': '2'}),
            data={'username': 'new_user'},
            content_type='application/json')
        assert resp.status_code == 405

        resp = self.client.delete(path=reverse(
            'api:chauser-detail',
            kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 405
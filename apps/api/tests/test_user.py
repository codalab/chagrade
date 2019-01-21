from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.profiles.models import Instructor

User = get_user_model()


class UsersAPIEndpointsTests(TestCase):

    def setUp(self):
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor

    def test_anonymous_user_cannot_perform_crud_method_on_users(self):
        resp = self.client.get(reverse('api:chauser-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(reverse('api:chauser-list', kwargs={'version': 'v1'}), data={'username': 'new_user'})
        assert resp.status_code == 401

        resp = self.client.put(
            reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}),
            data={'username': 'new_user'
                  },
            content_type='application/json'
        )
        assert resp.status_code == 401

        resp = self.client.delete(reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 401

    def test_student_user_can_only_get_users(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(reverse('api:chauser-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(reverse('api:chauser-list', kwargs={'version': 'v1'}), data={'username': 'new_user'})
        assert resp.status_code == 405

        resp = self.client.put(
            reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}),
            data={'username': 'new_user'}
        )
        assert resp.status_code == 405

        resp = self.client.delete(reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 405

    def test_instructor_user_can_only_get_users(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('api:chauser-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(reverse('api:chauser-list', kwargs={'version': 'v1'}), data={'username': 'new_user'})
        assert resp.status_code == 405

        resp = self.client.put(
            reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': '2'}),
            data={'username': 'new_user'
                  },
            content_type='application/json'
        )
        assert resp.status_code == 405

        resp = self.client.delete(reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 405

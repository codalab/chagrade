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
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.klass = Klass.objects.create(
            instructor=self.instructor,
            course_number="1")
        self.student = StudentMembership.objects.create(
            user=self.student_user,
            klass=self.klass,
            student_id='test_id')
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='test',
            description='test',
            challenge_url='')
        self.submission = Submission.objects.create(
            definition=self.definition,
            klass=self.klass,
            creator=self.student)
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.main_user.set_password('pass')
        self.main_user.save()
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()

    def test_anonymous_permissions(self):
        resp = self.client.get(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}),
            data={'username': 'new_user'})
        assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:studentmembership-detail',
            kwargs={'version': 'v1', 'pk': self.student_user.pk}),
            data={'student_id': 'student_23'},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse(
            'api:studentmembership-detail',
            kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 401

    def test_authenticated_permissions(self):  # Issue passing in user/submitted homeworks
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}),
            data={'user': [{self.student_user.pk}],
                  'student_id': 'student_23',
                  'klass': self.klass.pk,
                  'submitted_homeworks': self.submission.pk})
        assert resp.status_code == 404

        # TODO: RE-VISIT PUT ON STUDENT (Fields on serializer are making it difficult)

        resp = self.client.put(path=reverse(
            'api:studentmembership-detail',
            kwargs={'version': 'v1', 'pk': self.student.pk}),
            data={'user': [{self.student_user.pk}],
                  'student_id': 'student_23',
                  'klass': self.klass.pk,
                  'submitted_homeworks': self.submission.pk},
            content_type='application/json')
        assert resp.status_code == 400

        resp = self.client.delete(path=reverse(
            'api:studentmembership-detail',
            kwargs={'version': 'v1', 'pk': self.student.pk}))
        assert resp.status_code == 204

    def test_instructor_permissions(self):  # Can't figure out what to pass for user/submitted homeworks
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:studentmembership-list',
            kwargs={'version': 'v1'}),
            data={'user': '',
                  'klass': self.klass.id,
                  'student_id': 'student_21',
                  'submitted_homeworks': ''})
        assert resp.status_code == 201

        resp = self.client.put(
            path=reverse(
                'api:studentmembership-detail',
                kwargs={'version': 'v1', 'pk': '2'}),
            data={'student_id': 'student_23'},
            content_type='application/json')
        assert resp.status_code == 200

        resp = self.client.delete(
            path=reverse(
                'api:studentmembership-detail',
                kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from apps.homework.models import Definition, Submission
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership

User = get_user_model()


class SubmissionAPIEndpointsTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.main_user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
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

    def test_anonymous_permissions(self):
        resp = self.client.get(path=reverse(
            'api:submission-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(path=reverse(
            'api:submission-list',
            kwargs={'version': 'v1'}),
            data={"klass": '',
                  "definition": '',
                  "creator": '',
                  "submission_github_url": "",
                  "method_name": "",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": ''})
        assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk': self.submission.pk}),
            data={"klass": '',
                  "definition": '',
                  "creator": '',
                  "submission_github_url": "",
                  "method_name": "",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": ''},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk': self.submission.pk}))
        assert resp.status_code == 401

    def test_authenticated_permissions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:submission-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:submission-list',
            kwargs={'version': 'v1'}),
            data={"klass": self.klass.pk,
                  "definition": self.definition.pk,
                  "creator": self.instructor.pk,
                  "submission_github_url": "",
                  "method_name": "",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": b'self.submission.definition'})
        assert resp.status_code == 201

        resp = self.client.put(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk': '2'}),
            data={"klass": '',
                  "definition": '',
                  "creator": '',
                  "submission_github_url": "",
                  "method_name": "",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": ''},
            content_type='application/json')
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

    def test_instructor_permissions(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:submission-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:submission-list',
            kwargs={'version': 'v1'}),
            data={"klass": self.klass.pk,
                  "definition": self.definition.pk,
                  "creator": self.instructor.pk,
                  "submission_github_url": "",
                  "method_name": "",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": b'self.submission.definition'})
        assert resp.status_code == 201

        resp = self.client.put(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk': '2'}),
            data={"klass": '',
                  "definition": '',
                  "creator": '',
                  "submission_github_url": "",
                  "method_name": "",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": ''},
            content_type='application/json')
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

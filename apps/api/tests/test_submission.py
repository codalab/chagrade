import json

import responses
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.homework.models import Definition, Submission
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership

User = get_user_model()


class SubmissionAPIEndpointsTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass', email='test@email.com')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.main_user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.student = StudentMembership.objects.create(
            user=self.student_user,
            klass=self.klass,
            student_id='test_id'
        )
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='test',
            description='test',
            challenge_url='http://example.com/competitions/1'
        )
        self.submission = Submission.objects.create(
            definition=self.definition,
            klass=self.klass,
            creator=self.student
        )

    def test_anonymous_user_cannot_perform_crud_methods_on_submissions(self):
        resp = self.client.get(reverse('api:submission-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(
            reverse('api:submission-list', kwargs={'version': 'v1'}),
            data={
                "klass": '',
                "definition": '',
                "creator": '',
                "github_url": "",
                "method_name": "",
                "method_description": "",
                "project_url": "",
                "publication_url": "",
                "question_answers": ''
            })
        assert resp.status_code == 401

        resp = self.client.put(
            reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': 1}),
            data={
                "klass": '',
                "definition": '',
                "creator": '',
                "github_url": "",
                "method_name": "",
                "method_description": "",
                "project_url": "",
                "publication_url": "",
                "question_answers": ''
            },
            content_type='application/json'
        )
        assert resp.status_code == 401

        resp = self.client.delete(reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': 1}))
        assert resp.status_code == 401

    @responses.activate
    def test_student_can_perform_crud_methods_on_submissions(self):
        """Student should be able to do all CRUD, where as an Instructor cannot PUT/DELETE submissions"""
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(reverse('api:submission-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission/sas',
            body=json.dumps({
                'id': 'competition/15595/submission/44798/4aba772a-a6c1-4e6f-a82b-fb9d23193cb6.zip',
                'url': 'https://github.com/Tthomas63/chagrade_test_submission'
            }),
            status=201
        )
        responses.add(
            responses.GET,
            url='https://github.com/Tthomas63/chagrade_test_submission/archive/master.zip',
            status=200,
            body=json.dumps({})
        )
        responses.add(
            responses.PUT,
            url='https://github.com/Tthomas63/chagrade_test_submission',
            status=200,
            body=json.dumps({'text': 'testtext'})
        )
        responses.add(
            responses.GET,
            url='http://example.com/api/competition/1/phases/',
            status=200,
            body=json.dumps([{'phases': [{'id': '1'}]}])
        )
        new_sub_pk = self.submission.pk + 1
        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission?description=Chagrade_Submission_{}&phase_id=1'
                .format(new_sub_pk),
            body=json.dumps({'id': '1'}),
            status=201
        )

        resp = self.client.post(
            reverse('api:submission-list', kwargs={'version': 'v1'}),
            data={
                "klass": self.klass.pk,
                "definition": self.definition.pk,
                "creator": self.student.pk,
                "github_url": "https://github.com/Tthomas63/chagrade_test_submission/archive/master.zip",
                "method_name": "student method",
            }
        )

        sub_id = resp.json()['id']

        assert resp.json()['method_name'] == 'student method'
        assert resp.status_code == 201

        responses.add(
            responses.PUT,
            url='http://0.0.0.0/api/v1/submissions/{}/'.format(sub_id),
            status=200,
            body=json.dumps([{}])
        )

        resp = self.client.put(
            reverse('api:submission-detail', kwargs={'version': 'v1', 'pk':  sub_id}),
            data={
                "klass": self.klass.pk,
                "definition": self.definition.pk,
                "creator": self.student.pk,
                "method_name": "new method name",
            },
            content_type='application/json'
        )
        assert resp.json()['method_name'] == 'new method name'
        assert resp.status_code == 200

        resp = self.client.delete(reverse('api:submission-detail', kwargs={'version': 'v1', 'pk':  sub_id}))
        assert resp.status_code == 204

    @responses.activate
    def test_instructor_user_can_only_perform_get_and_post_methods_on_submissions(self):
        """Instructor cannot PUT/DELETE submissions, Student should be able to do all CRUD"""
        self.client.login(username='user', password='pass')

        resp = self.client.get(reverse('api:submission-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission/sas',
            body=json.dumps({
                'id': 'competition/15595/submission/44798/4aba772a-a6c1-4e6f-a82b-fb9d23193cb6.zip',
                'url': 'https://github.com/Tthomas63/chagrade_test_submission'
            }),
            status=201
        )
        responses.add(
            responses.GET,
            url='https://github.com/Tthomas63/chagrade_test_submission/archive/master.zip',
            status=200,
            body=json.dumps({})
        )
        responses.add(
            responses.PUT,
            url='https://github.com/Tthomas63/chagrade_test_submission',
            status=200,
            body=json.dumps({'text': 'testtext'})
        )
        responses.add(
            responses.GET,
            url='http://example.com/api/competition/1/phases/',
            status=200,
            body=json.dumps([{'phases': [{
                'id': '1'
            }]}]))

        new_sub_pk = self.submission.pk + 1
        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission?description=Chagrade_Submission_{}&phase_id=1'.format(
                new_sub_pk),
            body=json.dumps({'id': '2'}),
            status=201
        )

        resp = self.client.post(
            reverse('api:submission-list', kwargs={'version': 'v1'}),
            data={
                "klass": self.klass.pk,
                "definition": self.definition.pk,
                "creator": self.student.pk,
                "github_url": "https://github.com/Tthomas63/chagrade_test_submission/archive/master.zip",
                "method_name": "instructor method",
            }
        )

        sub_id = resp.json()['id']
        assert resp.json()['method_name'] == 'instructor method'
        assert resp.status_code == 201

        responses.add(
            responses.PUT,
            url='http://0.0.0.0/api/v1/submissions/{}/'.format(sub_id),
            status=200,
            body=json.dumps([{}])
        )
        resp = self.client.put(
            reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': sub_id}),
            data={
                "klass": self.klass.pk,
                "definition": self.definition.pk,
                "creator": self.student.pk,
                "method_name": "new method name"
            },
            content_type='application/json'
        )
        assert resp.status_code == 403

        resp = self.client.delete(reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': sub_id}))
        assert resp.status_code == 403

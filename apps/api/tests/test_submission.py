import json
import responses
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
        self.main_user = User.objects.create_user(
            username='user',
            password='pass'
        )
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
            kwargs={'version': 'v1', 'pk': 1}),
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
            kwargs={'version': 'v1', 'pk': 1}))
        assert resp.status_code == 401

    @responses.activate
    def test_authenticated_permissions(self):
        self.client.login(
            username='student_user',
            password='pass'
        )
        resp = self.client.get(
            path=reverse(
                'api:submission-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission/sas',
            body=json.dumps({
                'id': '1',
                'url': 'https://github.com/Tthomas63/chagrade_test_submission'
            }),
            status=201)

        responses.add(
            responses.GET,
            url='https://github.com/Tthomas63/chagrade_test_submission/archive/master.zip',
            status=200,
            body=json.dumps({}))

        responses.add(
            responses.PUT,
            url='https://github.com/Tthomas63/chagrade_test_submission',
            status=200,
            body=json.dumps({'text': 'testtext'}))
        responses.add(
            responses.GET,
            url='http://example.com/api/competition/1/phases/',
            status=200,
            body=json.dumps([{'phases': [{
                'id': '1'}]}]))

        new_sub_pk = self.submission.pk + 1
        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission?description=Chagrade_Submission_{}&phase_id=1'
            .format(new_sub_pk),
            body=json.dumps({'id': '1'}),
            status=201
        )

        resp = self.client.post(
            path=reverse('api:submission-list', kwargs={'version': 'v1'}),
            data={"klass": self.klass.pk,
                  "definition": self.definition.pk,
                  "creator": self.student.pk,
                  "submission_github_url": "https://github.com/Tthomas63/chagrade_test_submission",
                  "method_name": "student method",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": 'http://www.example3.com/anotherexample/1'
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

        resp = self.client.put(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk':  sub_id}),
            data={"klass": self.klass.pk,
                  "definition": self.definition.pk,
                  "creator": self.student.pk,
                  "method_name": "new method name",
                  },
            content_type='application/json')
        assert resp.json()['method_name'] == 'new method name'
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk':  sub_id}))
        assert resp.status_code == 204

    @responses.activate
    def test_instructor_permissions(self):
        self.client.login(username='user', password='pass')

        resp = self.client.get(
            path=reverse('api:submission-list', kwargs={'version': 'v1'})
        )
        assert resp.status_code == 200

        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission/sas',
            body=json.dumps({
                'id': 'https://github.com/Tthomas63/chagrade_test_submission',
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
            path=reverse('api:submission-list', kwargs={'version': 'v1'}),
            data={"klass": self.klass.pk,
                  "definition": self.definition.pk,
                  "creator": self.student.pk,
                  "submission_github_url": "https://github.com/Tthomas63/chagrade_test_submission",
                  "method_name": "instructor method",
                  "method_description": "",
                  "project_url": "",
                  "publication_url": "",
                  "question_answers": 'http://www.example3.com/anotherexample/1'
                  }
        )
        sub_id = resp.json()['id']
        assert resp.json()['method_name'] == 'instructor method'
        assert resp.status_code == 201

        responses.add(
            responses.PUT,
            url='http://0.0.0.0/api/v1/submissions/2/',
            status=200,
            body=json.dumps([{}])
        )

        resp = self.client.put(path=reverse(
            'api:submission-detail',
            kwargs={'version': 'v1', 'pk': sub_id}),
            data={"klass": self.klass.pk,
                  "definition": self.definition.pk,
                  "creator": self.student.pk,
                  "method_name": "new method name"
                  },
            content_type='application/json')
        assert resp.status_code == 403

        resp = self.client.delete(
            path=reverse(
                'api:submission-detail',
                kwargs={'version': 'v1', 'pk': sub_id
                        }))
        assert resp.status_code == 403

import json
import os
from unittest.mock import patch

import responses
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.homework.models import Definition, Submission, Grade
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
            challenge_url='http://example.com/competitions/1',
        )
        self.jupyter_notebook_definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='jupyter_notebook_test',
            description='jupyter_notebook_test',
            jupyter_notebook_enabled=True,
            jupyter_notebook_highest=10.0,
            jupyter_notebook_lowest=0.0,
            starting_kit_github_url='http://github.com/fake_starting_kit',
        )
        self.submission = Submission.objects.create(
            definition=self.definition,
            klass=self.klass,
            creator=self.student
        )

        self.test_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'files/test_submission.zip'
        )

        self.single_match_notebook = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'files/valid_notebook.ipynb'
        )

        self.no_matches_notebook = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'files/no_score_string_matches.ipynb'
        )

        self.multiple_matches_notebook = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'files/multiple_score_string_matches.ipynb'
        )

        self.score_too_low_notebook = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'files/score_too_low_notebook.ipynb'
        )

        self.score_too_high_notebook = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'files/score_too_high_notebook.ipynb'
        )

        assert os.path.exists(self.test_file_path)
        assert os.path.exists(self.single_match_notebook)
        assert os.path.exists(self.multiple_matches_notebook)
        assert os.path.exists(self.score_too_low_notebook)
        assert os.path.exists(self.score_too_high_notebook)

    def _direct_file_upload_helper(self, filename, definition):
        with open(filename, 'rb') as submission_file:
            resp = self.client.post(
                reverse('api:submission-list', kwargs={'version': 'v1'}),
                data={
                    "klass": self.klass.pk,
                    "definition": definition.pk,
                    "creator": self.student.pk,
                    "file": submission_file,
                    "method_name": "instructor method",
                }
            )
            return resp

    def add_all_responses(self):
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
            body=json.dumps([{'phases': [{'id': '1', 'is_active': True}]}])
        )
        new_sub_pk = self.submission.pk + 1
        responses.add(
            responses.POST,
            url='http://example.com/api/competition/1/submission?description=Chagrade_Submission_{}&phase_id=1'
                .format(new_sub_pk),
            body=json.dumps({'id': '1'}),
            status=201
        )

    @responses.activate
    def test_maximum_submissions_per_user_limit(self):
        self.add_all_responses()

        self.client.login(username='student_user', password='pass')
        resp = self.client.get(reverse('api:submission-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        definition_for_submission_limits = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='Sub Limits',
            description='test',
            challenge_url='http://example.com/competitions/1',
            max_submissions_per_student=1,
        )

        with patch('apps.api.views.homework.post_submission') as post_submission:
            # First submission POST should work.
            resp1 = self.client.post(
                reverse('api:submission-list', kwargs={'version': 'v1'}),
                data={
                    "klass": self.klass.pk,
                    "definition": definition_for_submission_limits.pk,
                    "creator": self.student.pk,
                    "github_url": "https://github.com/Tthomas63/chagrade_test_submission/archive/master.zip",
                    "method_name": "student method",
                }
            )

            assert post_submission.called
            assert resp1.status_code == 201

            # Second submission POST should get permission denied error (403) due to hitting submission limit.
            resp2 = self.client.post(
                reverse('api:submission-list', kwargs={'version': 'v1'}),
                data={
                    "klass": self.klass.pk,
                    "definition": definition_for_submission_limits.pk,
                    "creator": self.student.pk,
                    "github_url": "https://github.com/Tthomas63/chagrade_test_submission/archive/master.zip",
                    "method_name": "student method",
                }
            )

            assert post_submission.called
            assert resp2.status_code == 403

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

        self.add_all_responses()

        with patch('apps.api.views.homework.post_submission') as post_submission:
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
            assert post_submission.called

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

        self.add_all_responses()

        with patch('apps.api.views.homework.post_submission') as post_submission:
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
            assert post_submission.called

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

    def test_cannot_submit_file_to_github_only_definition(self):
        self.client.login(username='student_user', password='pass')

        self.definition.force_github = True
        self.definition.save()

        resp = self._direct_file_upload_helper(self.test_file_path, self.definition)
        assert resp.status_code == 400
        assert resp.content.decode('UTF-8') == '"This homework only takes github submissions!"'

    def test_can_submit_direct_upload_file(self):
        self.client.login(username='student_user', password='pass')

        with patch('apps.api.views.homework.post_submission') as post_submission:
            resp = self._direct_file_upload_helper(self.test_file_path, self.definition)
            assert resp.status_code == 201
            assert post_submission.called

    def test_successfully_submit_valid_jupyter_notebook(self):
        self.client.login(username='student_user', password='pass')

        resp = self._direct_file_upload_helper(self.single_match_notebook, self.jupyter_notebook_definition)
        new_submission_id = int(resp.json()['id'])
        new_submission = Submission.objects.get(pk=new_submission_id)
        assert new_submission.jupyter_score == 9.0
        assert resp.status_code == 201

    def test_successfully_submit_jupyter_notebook_with_multiple_score_string_matches(self):
        self.client.login(username='student_user', password='pass')

        # submit file to submission API with jupyter homework definition
        resp = self._direct_file_upload_helper(self.multiple_matches_notebook, self.jupyter_notebook_definition)
        new_submission_id = int(resp.json()['id'])
        new_submission = Submission.objects.get(pk=new_submission_id)
        assert new_submission.jupyter_score == 2.0
        assert resp.status_code == 201

    def test_successfully_submit_jupyter_notebook_with_no_score_string_matches(self):
        self.client.login(username='student_user', password='pass')

        # submit file to submission API with jupyter homework definition
        resp = self._direct_file_upload_helper(self.no_matches_notebook, self.jupyter_notebook_definition)
        new_submission_id = int(resp.json()['id'])
        new_submission = Submission.objects.get(pk=new_submission_id)
        assert new_submission.jupyter_score == new_submission.definition.jupyter_notebook_lowest
        assert resp.status_code == 201

    def test_successfully_submit_jupyter_notebook_with_score_too_low(self):
        self.client.login(username='student_user', password='pass')

        # submit file to submission API with jupyter homework definition
        resp = self._direct_file_upload_helper(self.score_too_low_notebook, self.jupyter_notebook_definition)
        new_submission_id = int(resp.json()['id'])
        new_submission = Submission.objects.get(pk=new_submission_id)
        assert new_submission.jupyter_score == new_submission.definition.jupyter_notebook_lowest
        assert resp.status_code == 201

    def test_successfully_submit_jupyter_notebook_with_score_too_high(self):
        self.client.login(username='student_user', password='pass')

        # submit file to submission API with jupyter homework definition
        resp = self._direct_file_upload_helper(self.score_too_high_notebook, self.jupyter_notebook_definition)
        new_submission_id = int(resp.json()['id'])
        new_submission = Submission.objects.get(pk=new_submission_id)
        assert new_submission.jupyter_score == new_submission.definition.jupyter_notebook_highest
        assert resp.status_code == 201

    def test_resubmission_does_not_affect_grade(self):
        self.client.login(username='student_user', password='pass')

        resp = self._direct_file_upload_helper(self.single_match_notebook, self.jupyter_notebook_definition)
        new_submission_id = int(resp.json()['id'])
        new_submission = Submission.objects.get(pk=new_submission_id)
        assert new_submission.jupyter_score == 9.0
        assert resp.status_code == 201

        grade = Grade.objects.create(submission=new_submission, jupyter_notebook_grade=177.0, evaluator=self.main_user.instructor)

        resp = self._direct_file_upload_helper(self.single_match_notebook, self.jupyter_notebook_definition)
        new_submission_id = int(resp.json()['id'])
        new_submission = Submission.objects.get(pk=new_submission_id)
        assert new_submission.jupyter_score == 9.0
        assert resp.status_code == 201

        assert new_submission.grades.last().jupyter_notebook_grade == grade.jupyter_notebook_grade

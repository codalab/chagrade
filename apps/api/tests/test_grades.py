from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from apps.homework.models import Definition, Submission, Grade
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership
User = get_user_model()


class GradesAPIEndpointsTests(TestCase):

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
            challenge_url=''
        )
        self.submission = Submission.objects.create(
            definition=self.definition,
            klass=self.klass,
            creator=self.student
        )
        self.grade = Grade.objects.create(
            evaluator=self.instructor,
            submission=self.submission
        )

    def test_anonymous_permissions(self):
        resp = self.client.get(path=reverse(
            'api:grade-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(path=reverse(
            'api:grade-list',
            kwargs={'version': 'v1'}),
            data={"submission": '',
                  "evaluator": '',
                  "teacher_comments": "",
                  "instructor_notes": "",
                  "criteria_answers": ''})
        assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:grade-detail',
            kwargs={'version': 'v1', 'pk': self.grade.pk}),
            data={"submission": '',
                  "evaluator": '',
                  "teacher_comments": "",
                  "instructor_notes": "",
                  "criteria_answers": ''},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse(
            'api:grade-detail',
            kwargs={'version': 'v1', 'pk': self.grade.pk}))
        assert resp.status_code == 401

    def test_authenticated_permissions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:grade-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:grade-list',
            kwargs={'version': 'v1'}),
            data={"submission": self.submission.pk,
                  "evaluator": self.instructor.pk,
                  "teacher_comments": "",
                  "instructor_notes": "testnotes",
                   "criteria_answers": ''})
        assert resp.json()['instructor_notes'] == 'testnotes'
        assert resp.status_code == 201

        new_grade_pk = resp.json()['id']
        resp = self.client.put(path=reverse(
            'api:grade-detail',
            kwargs={'version': 'v1', 'pk': new_grade_pk}),
            data={"submission": self.submission.pk,
                  "evaluator": self.instructor.pk,
                  "teacher_comments": "",
                  "instructor_notes": "changed instructor notes"},
            content_type='application/json')
        assert resp.status_code == 403

        resp = self.client.delete(path=reverse(
            'api:grade-detail',
            kwargs={'version': 'v1', 'pk': new_grade_pk}))
        assert resp.status_code == 403

    def test_instructor_permissions(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:grade-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:grade-list',
            kwargs={'version': 'v1'}),
            data={"submission": self.submission.pk,
                  "evaluator": self.instructor.pk,
                  "teacher_comments": "",
                  "instructor_notes": "testnotes",
                  "criteria_answers": ''})
        assert resp.json()['instructor_notes'] == 'testnotes'
        assert resp.status_code == 201

        new_grade_pk = resp.json()['id']
        resp = self.client.put(path=reverse(
            'api:grade-detail',
            kwargs={'version': 'v1', 'pk': new_grade_pk}),
            data={"submission": self.submission.pk,
                  "evaluator": self.instructor.pk,
                  "teacher_comments": "",
                  "instructor_notes": "changed instructor notes"},
            content_type='application/json')
        assert resp.json()["instructor_notes"] == 'changed instructor notes'
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse(
            'api:grade-detail',
            kwargs={'version': 'v1', 'pk': new_grade_pk}))
        assert resp.status_code == 204

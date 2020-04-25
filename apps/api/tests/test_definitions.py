from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from apps.homework.models import Definition, Criteria, Submission, Grade, CriteriaAnswer
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership

User = get_user_model()


class DefinitionAPIEndpointsTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass', email='test@email.com')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.definition = Definition.objects.create(klass=self.klass, creator=self.instructor, name='test_def_1', description='A simple test', due_date=timezone.now())

    def test_anonymous_user_cannot_perform_crud_methods_on_definitions(self):
        resp = self.client.get(reverse('api:definition-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(
            reverse('api:definition-list', kwargs={'version': 'v1'}),
            data={
                'klass': self.klass.pk,
                'creator': self.instructor.pk,
                'due_date': timezone.now(),
                'name': 'test',
                'description': 'test'
            }
        )
        assert resp.status_code == 401

        resp = self.client.put(
            reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': 1}),
            data={'name': 'A Different Name'},
            content_type='application/json'
        )
        assert resp.status_code == 401

        resp = self.client.delete(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': 1}))
        assert resp.status_code == 401

    def test_student_user_can_only_post_and_get_definitions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(reverse('api:definition-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(
            reverse('api:definition-list', kwargs={'version': 'v1'}),
            data={
                'klass': self.klass.pk,
                'creator': self.instructor.pk,
                'due_date': timezone.now(),
                'name': 'test1',
                'description': 'test'
            }
        )
        # posted_url = resp.json()['id']
        assert resp.status_code == 403
        # assert resp.json()['name'] == 'test1'

        resp = self.client.put(
            reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.definition.pk}),
            data={
                'name': 'A Different Name',
                'klass': self.klass.pk,
                'creator': self.instructor.pk
            },
            content_type='application/json'
        )
        assert resp.status_code == 403

        resp = self.client.delete(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.definition.pk}))
        assert resp.status_code == 403

    def test_instructor_user_can_get_and_post_on_definitions(self):
        self.client.login(username='user', password='pass')

        resp = self.client.get(reverse('api:definition-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(
            reverse('api:definition-list', kwargs={'version': 'v1'}),
            data={
                'klass': self.klass.pk,
                'creator': self.instructor.pk,
                'due_date': timezone.now(),
                'name': 'test_definition',
                'description': 'test'
                  }
        )
        d_pk = resp.json()['id']
        data = resp.json()
        assert data['name'] == 'test_definition'
        assert resp.status_code == 201

        resp = self.client.put(
            reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': d_pk}),
            data={
                'name': 'A Different Name',
                'klass': self.klass.pk,
                'creator': self.instructor.pk
            },
            content_type='application/json'
        )
        assert resp.status_code == 200

        resp = self.client.delete(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': d_pk}))
        assert resp.status_code == 204

    def test_avg_grade_is_correct(self):
        self.criteria = Criteria.objects.create(
            definition=self.definition,
            lower_range=0,
            upper_range=5,
        )
        for i in range(5):
            self.student_user = User.objects.create_user(username=f'student_user{i}', password='pass', email=f'test{i}@email.com')
            self.student = StudentMembership.objects.create(
                user=self.student_user,
                klass=self.klass,
                student_id=f"{i}",
            )
            self.submission = Submission.objects.create(
                definition=self.definition,
                klass=self.klass,
                creator=self.student,
            )
            self.grade = Grade.objects.create(
                submission=self.submission,
                evaluator=self.instructor,
            )
            self.criteria_answer = CriteriaAnswer.objects.create(
                grade=self.grade,
                criteria=self.criteria,
                score=i,
            )
            print(i)
        assert self.definition.avg_grade() == "40.0%"



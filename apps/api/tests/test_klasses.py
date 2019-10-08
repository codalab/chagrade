from io import StringIO
import csv
import pprint

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership

from apps.factory.factories import DefinitionFactory, SubmissionFactory, QuestionFactory, QuestionAnswerFactory, StudentMembershipFactory


User = get_user_model()


class KlassesAPIEndpointTests(TestCase):

    def setUp(self):

        self.main_user = User.objects.create_user(username='user', password='pass', email='test@email.com')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.student = StudentMembership.objects.create(user=self.student_user, klass=self.klass, student_id='test_id')
        self.definition = DefinitionFactory(klass=self.klass, questions_only=True)

        # Total of 4 students
        self.student_quantity = 4
        for i in range(3):
            StudentMembershipFactory(klass=self.klass)

        # Total of 10 questions
        self.question_quantity = 10
        questions = []
        for i in range(self.question_quantity):
            questions.append(QuestionFactory(definition=self.definition))

        # Create answers to each question for each student
        for student in self.klass.enrolled_students.all():
            submission = SubmissionFactory(creator=student, definition=self.definition, klass=self.klass)
            for i in range(self.question_quantity):
                QuestionAnswerFactory(submission=submission, question=questions[i])

    def test_anonymous_user_cannot_perform_crud_methods_on_klasses(self):
        resp = self.client.get(reverse('api:klass-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(
            reverse('api:klass-list', kwargs={'version': 'v1'}),
            data={
                'title': 'Test',
                'instructor': self.instructor.pk
            }
        )
        assert resp.status_code == 401

        resp = self.client.put(
            reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': self.klass.pk}),
            data={'title': 'A Different Name'}, content_type='application/json'
        )
        assert resp.status_code == 401

        resp = self.client.delete(reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': self.klass.pk}))
        assert resp.status_code == 401

    def test_student_user_can_get_and_post_klasses(self): # Currently not working as intended
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(reverse('api:klass-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(
            reverse('api:klass-list', kwargs={'version': 'v1'}),
            data={
                'title': 'Test',
                'instructor': self.instructor.pk,
                'course_number': self.klass.pk
            }
        )
        assert resp.status_code == 403

        new_klass_pk = self.klass.pk + 1
        resp = self.client.put(
            reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': new_klass_pk}),
            data={
                'title': 'A Different Name',
                'instructor': self.instructor.pk,
                'course_number': 1
            },
            content_type='application/json'
        )
        assert resp.status_code == 403

        resp = self.client.delete(reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': new_klass_pk}))
        assert resp.status_code == 403

    def test_instructor_user_can_get_and_post_klasses(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(reverse('api:klass-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(
            reverse('api:klass-list', kwargs={'version': 'v1'}),
            data={
                'title': 'Test',
                'instructor': self.instructor.pk,
                'course_number': 2

            }
        )
        data = resp.json()
        assert resp.status_code == 201
        assert data['title'] == 'Test'

        new_klass_pk = self.klass.pk + 1
        resp = self.client.put(
            reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': new_klass_pk}),
            data={
                'title': 'A Different Name',
                'instructor': self.instructor.pk,
                'course_number': 2
            },
            content_type='application/json'
        )
        assert resp.status_code == 200

        resp = self.client.delete(reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': new_klass_pk}))
        assert resp.status_code == 204

    def test_anonymous_user_cannot_get_homework_answers(self):
        request_kwargs = {
            'version': 'v1',
            'definition_pk': self.definition.pk,
            'klass_pk': self.klass.pk,
        }

        resp = self.client.get(reverse('api:homework_answers_CSV', kwargs=request_kwargs))
        assert resp.status_code == 401

    def test_students_cannot_get_homework_answers(self):
        self.client.login(username='student_user', password='pass')
        request_kwargs = {
            'version': 'v1',
            'definition_pk': self.definition.pk,
            'klass_pk': self.klass.pk,
        }

        resp = self.client.get(reverse('api:homework_answers_CSV', kwargs=request_kwargs))

        assert resp.status_code == 403

    def test_instructors_can_get_homework_answers(self):
        self.client.login(username='user', password='pass')
        request_kwargs = {
            'version': 'v1',
            'definition_pk': self.definition.pk,
            'klass_pk': self.klass.pk,
        }

        resp = self.client.get(reverse('api:homework_answers_CSV', kwargs=request_kwargs))

        assert resp.status_code == 200

    def test_homework_answers_endpoint_returns_properly_shaped_csv(self):
        self.client.login(username='user', password='pass')
        request_kwargs = {
            'version': 'v1',
            'definition_pk': self.definition.pk,
            'klass_pk': self.klass.pk
        }

        resp = self.client.get(reverse('api:homework_answers_CSV', kwargs=request_kwargs))

        f = StringIO(resp.content.decode('utf-8'))
        csv_list = csv.reader(f, delimiter=',')

        # Initialize row count with -1 to offset labels row
        row_count = -1
        for row in csv_list:
            row_count += 1

            # Initialize column count with -1 to offset name field
            column_count = -1
            for column in row:
                column_count += 1
            assert column_count == self.question_quantity
        assert row_count == self.student_quantity

from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse
from django.utils import timezone

from apps.groups.models import Team
from apps.homework.models import Definition, Criteria, Submission, Question, Grade, CriteriaAnswer
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership

User = get_user_model()


class AnonymousUserPermissionTests(TestCase):

    def setUp(self):
        self.instructor = Instructor.objects.create(university_name='Test')
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.student = StudentMembership.objects.create(user=self.student_user, klass=self.klass, student_id='test_id')
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='test',
            description='test'
        )
        self.question = Question.objects.create(
            definition=self.definition,
            question='Test Question',
            answer='Test Answer'
        )
        self.criteria = Criteria.objects.create(
            definition=self.definition,
            description='Test Criteria',
            lower_range=0,
            upper_range=10
        )
        self.submission = Submission.objects.create(
            definition=self.definition,
            klass=self.klass,
            creator=self.student
        )
        self.team = Team.objects.create(
            klass=self.klass
        )
        self.grade = Grade.objects.create(
            evaluator=self.instructor,
            submission=self.submission
        )
        self.criteria_answers = CriteriaAnswer.objects.create(
            grade=self.grade,
            criteria_id=self.criteria.id,
            criteria=self.criteria)

    @tag('passing')
    def test_crud_methods_on_users(self):
        #  Tests that we can't find a list of users, or change anything about them
        resp = self.client.get(path=reverse('api:chauser-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new user
        resp = self.client.post(path=reverse('api:chauser-list', kwargs={'version': 'v1'}), data={'username': 'new_user'})
        assert resp.status_code == 401

        #  Tests that we can't change a current user
        resp = self.client.put(path=reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}),
                               data={'username': 'new_user'},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete a user
        resp = self.client.delete(path=reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_students(self):
        #  Tests that we can't retrieve a list of students
        resp = self.client.get(path=reverse('api:studentmembership-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new student
        resp = self.client.post(path=reverse('api:studentmembership-list', kwargs={'version': 'v1'}),
                                data={'username': 'new_user'})
        assert resp.status_code == 401

        #  Tests that we can't change info of a student
        resp = self.client.put(path=reverse('api:studentmembership-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}),
                               data={'student_id': 'student_23'},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete a student
        resp = self.client.delete(path=reverse('api:studentmembership-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_klasses(self):
        #  Tests that we can't retrieve a list of klasses
        resp = self.client.get(path=reverse('api:klass-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new klass
        resp = self.client.post(path=reverse('api:klass-list', kwargs={'version': 'v1'}),
                                data={'title': 'Test', 'instructor': self.instructor.pk})
        assert resp.status_code == 401

        #  Tests that we can't change info of a klass
        resp = self.client.put(path=reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': self.klass.pk}),
                               data={'title': 'A Different Name'},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete a klass
        resp = self.client.delete(path=reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': self.klass.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_definitions(self):
        #  Tests that we can't retrieve a list of definitions
        resp = self.client.get(path=reverse('api:definition-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new definition
        resp = self.client.post(path=reverse('api:definition-list', kwargs={'version': 'v1'}),
                                data={'klass': self.klass.pk,
                                'creator': self.instructor.pk,
                                'due_date': timezone.now(),
                                'name': 'test',
                                'description': 'test'})
        assert resp.status_code == 401

        #  Tests that we can't change a definition
        resp = self.client.put(path=reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.definition.pk}),
                               data={'name': 'A Different Name'},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete a definition
        resp = self.client.delete(reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': self.definition.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_criterias(self):
        #  Tests that we can't retrieve a list of criteria
        resp = self.client.get(path=reverse('api:criteria-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post new criteria
        resp = self.client.post(path=reverse('api:criteria-list', kwargs={'version': 'v1'}),
                                data={'description': 'test',
                                      'lower_range': 0,
                                      'upper_range': 10})
        assert resp.status_code == 401

        #  Tests that we can't change a criteria
        resp = self.client.put(path=reverse('api:criteria-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}),
                               data={'description': 'test',
                                     'lower_range': 0,
                                     'upper_range': 10},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete a criteria
        resp = self.client.delete(path=reverse('api:criteria-detail', kwargs={'version': 'v1', 'pk': self.criteria.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_questions(self):
        #  Tests that we can't retrieve a list of questions
        resp = self.client.get(path=reverse('api:question-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new question
        resp = self.client.post(path=reverse('api:question-list', kwargs={'version': 'v1'}),
                                data={"has_specific_answer": False,
                                      "question": "testquestion",
                                      "answer": "testanswer",
                                      "definition_id": self.definition.id})
        assert resp.status_code == 401

        #  Tests that we can't change a question
        resp = self.client.put(path=reverse('api:question-detail', kwargs={'version': 'v1', 'pk': self.question.pk}),
                               data={"has_specific_answer": False,
                                     "question": "testquestion",
                                     "answer": "testanswer",
                                     "definition_id": self.definition.id},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete a question
        resp = self.client.delete(path=reverse('api:question-detail', kwargs={'version': 'v1', 'pk': self.question.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_submissions(self):
        #  Tests that we can't retrieve a list of submissions using get method
        resp = self.client.get(path=reverse('api:submission-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new submission
        resp = self.client.post(path=reverse('api:submission-list', kwargs={'version': 'v1'}),
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
        #  Tests that we can't change any submissions info using put method
        resp = self.client.put(path=reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': self.submission.pk}),
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

        #  Tests that we can't delete any submissions
        resp = self.client.delete(path=reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': self.submission.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_grades(self):
        #  Tests that we can't retrieve a list of grades using get method
        resp = self.client.get(path=reverse('api:grade-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new grade
        resp = self.client.post(path=reverse('api:grade-list', kwargs={'version': 'v1'}),
                                data={"submission": '',
                                      "evaluator": '',
                                      "teacher_comments": "",
                                      "instructor_notes": "",
                                      "criteria_answers": ''})
        assert resp.status_code == 401

        #  Tests that we can't change any grade info using put method
        resp = self.client.put(path=reverse('api:grade-detail', kwargs={'version': 'v1', 'pk': self.grade.pk}),
                               data={"submission": '',
                                     "evaluator": '',
                                     "teacher_comments": "",
                                     "instructor_notes": "",
                                     "criteria_answers": ''},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete any grade
        resp = self.client.delete(path=reverse('api:grade-detail', kwargs={'version': 'v1', 'pk': self.grade.pk}))
        assert resp.status_code == 401

    @tag('passing')
    def test_crud_methods_on_teams(self):
        #  Tests that we can't retrieve a list of team using get method
        resp = self.client.get(path=reverse('api:team-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        #  Tests that we can't post a new team
        resp = self.client.post(path=reverse('api:team-list', kwargs={'version': 'v1'}),
                                data={"klass": '',
                                      "name": "",
                                      "description": "",
                                      "members": ''})
        assert resp.status_code == 401

        #  Tests that we can't change any team info using put method
        resp = self.client.put(path=reverse('api:team-detail', kwargs={'version': 'v1', 'pk': self.team.pk}),
                               data={"klass": '',
                                     "name": "",
                                     "description": "",
                                     "members": ''},
                               content_type='application/json')
        assert resp.status_code == 401

        #  Tests that we can't delete any teams
        resp = self.client.delete(path=reverse('api:team-detail', kwargs={'version': 'v1', 'pk': self.team.pk}))
        assert resp.status_code == 401
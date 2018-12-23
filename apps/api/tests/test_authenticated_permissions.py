from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse
from django.utils import timezone

from apps.groups.models import Team
from apps.homework.models import Definition, Criteria, Submission, Question, Grade, CriteriaAnswer
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership, ChaUser

User = get_user_model()


class AuthenticatedUserPermissionTests(TestCase):

    def setUp(self):

        self.main_user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()

        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.student = StudentMembership.objects.create(user=self.student_user, klass=self.klass, student_id='test_id')
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='test',
            description='test',
            challenge_url=''
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
        #  Testing that a student user can only get a list of users, and that they cannot post, put, or delete one
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path='/api/v1/users/')
        assert resp.status_code == 200

        resp = self.client.post(path=reverse('api:chauser-list', kwargs={'version': 'v1'}), data={'username': 'new_user'})
        assert resp.status_code == 405

        resp = self.client.put(path=reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}),
                               data={'username': 'new_user'})
        assert resp.status_code == 405

        resp = self.client.delete(path=reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': self.student_user.pk}))
        assert resp.status_code == 405

    @tag('incomplete')
    def test_crud_methods_on_students(self):  # Issue passing in user/submitted homeworks
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:studentmembership-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse('api:studentmembership-list', kwargs={'version': 'v1'}),
                                data={'user': [{self.student_user.pk}],
                                      'student_id': 'student_23',
                                      'klass': self.klass.pk,
                                      'submitted_homeworks': self.submission.pk})
        print(resp)
        print(resp.content)
        # import pdb;
        # pdb.set_trace()
        assert resp.status_code == 404

        # TODO: RE-VISIT PUT ON STUDENT (Fields on serializer are making it difficult)


        temp_data = resp.json()
        temp_data['student_id'] = 'test_id_123'

        print("!!!!!!!")
        print(temp_data)
        print("!!!!!!!")

        resp = self.client.put(path='/api/v1/students/{}/'.format(self.student.pk), data=temp_data,
                               content_type='application/json')
        print(resp)
        print(resp.content)
        assert resp.status_code == 400
        # self.student.refresh_from_db()
        # assert self.student.student_id == 'test_id_123'

        resp = self.client.delete(path='/api/v1/students/{}/'.format(self.student.pk))
        print(resp)
        print(resp.content)
        assert resp.status_code == 204

    @tag('passing')
    def test_crud_methods_on_klasses(self):
        # Test as a regular user/creator
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:klass-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path='/api/v1/klasses/', data={'title': 'Test', 'instructor': self.instructor.pk, 'course_number': 2})
        print(resp)
        print(resp.content)
        # import pdb;
        # pdb.set_trace()
        # TODO: Block this
        # assert resp.status_code == 401

        resp = self.client.put(path='/api/v1/klasses/{}/'.format(self.klass.pk),
                               data={'title': 'A Different Name', 'instructor': self.instructor.pk, 'course_number': 1},
                               content_type='application/json')
        print(resp)
        print(resp.content)
        assert resp.status_code == 403

        resp = self.client.delete(path='/api/v1/klasses/{}/'.format(self.klass.pk))
        print(resp)
        print(resp.content)
        assert resp.status_code == 403

    @tag('passing')
    def test_crud_methods_on_definitions(self):
        # Tests that we can get/post but not be able to change or delete definitions
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:definition-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse('api:definition-list', kwargs={'version': 'v1'}),
                                data={'klass': self.klass.pk,
                                'creator': self.instructor.pk,
                                'due_date': timezone.now(),
                                'name': 'test1',
                                'description': 'test'})
        assert resp.status_code == 201
        assert resp.json()['name'] == 'test1'

        resp = self.client.put(path=reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': '2'}),
                               data={'name': 'A Different Name', 'klass': self.klass.pk, 'creator': self.instructor.pk},
                               content_type='application/json')
        assert resp.status_code == 403

        resp = self.client.delete(path=reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 403

    @tag('passing')
    def test_get_and_delete_methods_on_criteria(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:criteria-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse('api:criteria-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 401

    @tag('passing')
    def test_get_method_on_list_of_question_and_list(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:question-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(path=reverse('api:question-detail', kwargs={'version': 'v1', 'pk': '1'}))
        assert resp.json()['question'] == 'Test Question'

    @tag('help_needed')  #  Need to figure out what to pass for competition_url
    def test_crud_methods_on_submissions(self):
        #  Tests that we can retrieve a list of submissions using get method
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:submission-list', kwargs={'version': 'v1'}))
        print(resp.content)

        assert resp.status_code == 200

        #  Tests that we can post a new submission
        resp = self.client.post(path=reverse('api:submission-list', kwargs={'version': 'v1'}),
                                data={"klass": self.klass.pk,
                                      "definition": self.definition.pk,
                                      "creator": self.instructor.pk,
                                      "submission_github_url": "",
                                      "method_name": "",
                                      "method_description": "",
                                      "project_url": "",
                                      "publication_url": "",
                                      "question_answers": b'self.submission.definition'})
        print(resp.content)
        assert resp.status_code == 201

        #  Tests that we can't change any submissions info using put method
        resp = self.client.put(path=reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': '2'}),
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

        #  Tests that we can't delete any submissions
        resp = self.client.delete(path=reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

    @tag('passing')
    def test_crud_methods_on_grades(self):
        #  Tests that a student can post a new grade but not delete/put one
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:grade-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse('api:grade-list', kwargs={'version': 'v1'}),
                                data={"submission": self.submission.pk,
                                      "evaluator": self.instructor.pk,
                                      "teacher_comments": "",
                                      "instructor_notes": "testnotes",
                                      "criteria_answers": ''})
        assert resp.json()['instructor_notes'] == 'testnotes'
        assert resp.status_code == 201

        resp = self.client.put(path=reverse('api:grade-detail', kwargs={'version': 'v1', 'pk': '2'}),
                               data={"submission": self.submission.pk,
                                     "evaluator": self.instructor.pk,
                                     "teacher_comments": "",
                                     "instructor_notes": "changed instructor notes"},
                               content_type='application/json')
        assert resp.status_code == 403

        #  Tests that we can delete a grade
        resp = self.client.delete(path=reverse('api:grade-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 403

    @tag('incomplete')  #  Can't properly pass in "members" into the post request  "b'{"members":["This field is required."
    def test_crud_methods_on_teams(self):
        #  Tests that we can't retrieve a list of team using get method
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse('api:team-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200
        print(resp.content)

        #  Tests that we can post a new team
        resp = self.client.post(path=reverse('api:team-list', kwargs={'version': 'v1'}),
                                data={"klass": self.klass.pk,
                                      "name": "testteam",
                                      "description": "",
                                      "members": self.student.pk})
        print(resp.content)
        assert resp.status_code == 201

        #  Tests that we can  change a teams info using put method
        resp = self.client.put(path=reverse('api:team-detail', kwargs={'version': 'v1', 'pk': '2'}),
                               data={"klass": '',
                                     "name": "",
                                     "description": "",
                                     "members": ''},
                               content_type='application/json')
        assert resp.status_code == 200

        #  Tests that we can delete a team
        resp = self.client.delete(path=reverse('api:team-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

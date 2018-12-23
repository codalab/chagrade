from django.contrib.auth import get_user_model
from django.test import TestCase, tag
from django.urls import reverse
from django.utils import timezone

from apps.groups.models import Team
from apps.homework.models import Definition, Criteria, Submission, Question, Grade, CriteriaAnswer
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership, ChaUser

User = get_user_model()


class InstructorUserPermissionsTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.main_user.set_password('pass')
        self.main_user.save()
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.main_user.save()

        # Once an instructor can't change a klass unless he's the owner - uncomment out this and the commented out
        # portion of test_crud_methods_on_klasses
        # self.alt_user = User.objects.create_user(username='altuser', password='pass')
        # self.alt_user.set_password('pass')
        # self.alt_user.save()
        # self.alt_instructor = Instructor.objects.create(university_name='Test2')
        # self.alt_user.instructor = self.alt_instructor
        # self.alt_user.save()

        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.student_user = User.objects.create_user(username='student_user', password='pass')

        self.team = Team.objects.create(klass=self.klass, name="teamname")
        self.student = StudentMembership.objects.create(
            user=self.student_user,
            klass=self.klass,
            student_id='test_id',
            team=self.team
        )
        self.definition = Definition.objects.create(
            klass=self.klass,
            creator=self.instructor,
            due_date=timezone.now(),
            name='test',
            description='test',
            challenge_url=''  #reverse('api:submission-detail', kwargs={'version': 'v1', 'pk': '2'})
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
        self.grade = Grade.objects.create(
            evaluator=self.instructor,
            submission=self.submission
        )
        self.criteria_answers = CriteriaAnswer.objects.create(
            grade=self.grade,
            criteria_id=self.criteria.id,
            criteria=self.criteria)

    @tag('passing')  # Can only get list - post/put/del not allowed
    def test_crud_methods_on_users(self):
        #  Tests that we can find a list of users
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:chauser-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        #  Tests that we can post a new user
        # resp = self.client.post(path=reverse('api:chauser-list', kwargs={'version': 'v1'}),
        #                         data={'username': 'new_user',
        #                               })
        # print(resp.content)
        # print(resp.status_code)
        # assert resp.status_code == 201

        #  Tests that we can change a current user
        # resp = self.client.put(path=reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': '2'}),
        #                        data={'username': 'new_user'},
        #                        content_type='application/json')
        # print(resp.content)
        # print(resp.status_code)
        # assert resp.status_code == 200

        #  Tests that we can delete a user
        # resp = self.client.delete(path=reverse('api:chauser-detail', kwargs={'version': 'v1', 'pk': '2'}))
        # print(resp.content)
        # print(resp.status_code)
        # assert resp.status_code == 204

    @tag('incomplete')
    def test_crud_methods_on_students(self):  # Can't figure out what to pass for user/submitted homeworks
        #  Tests that we can't retrieve a list of students
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:studentmembership-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        #  Tests that we can't post a new student
        resp = self.client.post(path=reverse('api:studentmembership-list', kwargs={'version': 'v1'}),
                                data={
                                    'user': '',
                                    'klass': self.klass.id,
                                    'student_id': 'student_21',
                                    'submitted_homeworks': ''})
        print(resp.content)
        print(resp.status_code)
        assert resp.status_code == 201

        #  Tests that we can't change info of a student
        resp = self.client.put(
            path=reverse('api:studentmembership-detail', kwargs={'version': 'v1', 'pk': '2'}),
            data={'student_id': 'student_23'},
            content_type='application/json')
        print(resp.content)
        print(resp.status_code)
        assert resp.status_code == 200

        #  Tests that we can't delete a student
        resp = self.client.delete(
            path=reverse('api:studentmembership-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

    @tag('passing')
    def test_crud_methods_on_klasses(self):   #  and_only_creator_can_put_owned_klass(self):
        # Tests an instructor can get/post/put/delete klasses.
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:klass-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse('api:klass-list', kwargs={'version': 'v1'}),
                                data={'title': 'Test', 'instructor': self.instructor.pk, 'course_number': 2})
        data = resp.json()
        assert resp.status_code == 201
        assert data['title'] == 'Test'

        #  Note to self:  Must put in pk=2 for the path as a klass object is already made in setUp, thus pk=1 won't work
        resp = self.client.put(path=reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': '2'}),
                               data={'title': 'A Different Name', 'instructor': self.instructor.pk, 'course_number': 2},
                               content_type='application/json')
        data = resp.json()
        assert resp.status_code == 200
        assert data['title'] == "A Different Name"

        resp = self.client.delete(path=reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

        #  The following portion of the test should be added once instructors can't modify other peoples klasses
        # resp = self.client.post(path=reverse('api:klass-list', kwargs={'version': 'v1'}),
        #                         data={'title': 'Test', 'instructor': self.instructor.pk, 'course_number': 2})
        # self.client.logout()
        # print(resp.status_code)
        # print(resp.content)
        # self.client.login(username='user', password='pass')
        # resp = self.client.put(path=reverse('api:klass-detail', kwargs={'version': 'v1', 'pk': '3'}),
        #                        data={'title': 'A Different Name', 'instructor': self.instructor.pk, 'course_number': 2},
        #                        content_type='application/json')
        # data = resp.json()
        # print(resp.status_code)
        # assert resp.status_code == 200
        # assert data['title'] == "A Different Name"

    @tag('passing')
    def test_crud_methods_on_definitions(self):
        #  Tests we can retrieve a list of definitions, then posts a new one, changes it, and deletes it
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:definition-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse('api:definition-list', kwargs={'version': 'v1'}),
                                data={'klass': self.klass.pk,
                                      'creator': self.instructor.pk,
                                      'due_date': timezone.now(),
                                      'name': 'test_definition',
                                      'description': 'test'})
        data = resp.json()
        assert data['name'] == 'test_definition'
        assert resp.status_code == 201

        resp = self.client.put(path=reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': '2'}),
                               data={'name': 'A Different Name', 'klass': self.klass.pk, 'creator': self.instructor.pk},
                               content_type='application/json')
        data = resp.json()
        assert data['name'] == 'A Different Name'
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse('api:definition-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

    @tag('passing')
    def test_get_method_on_list_of_criteria_and_list(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:criteria-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(path=reverse('api:criteria-detail', kwargs={'version': 'v1', 'pk': '1'}))
        assert resp.json()['description'] == 'Test Criteria'

    @tag('passing')
    def test_get_method_on_list_of_question_and_list(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:question-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.get(path=reverse('api:question-detail', kwargs={'version': 'v1', 'pk': '1'}))
        assert resp.json()['question'] == 'Test Question'

    @tag('help_needed')  #  Need to figure out what to pass for competition_url
    def test_crud_methods_on_submissions(self):
        #  Tests that we can retrieve a list of submissions using get method
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:submission-list', kwargs={'version': 'v1'}))
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
        #  Tests that we can retrieve a list of grades using get method
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:grade-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        #  Tests that we can post a new grade
        resp = self.client.post(path=reverse('api:grade-list', kwargs={'version': 'v1'}),
                                data={"submission": self.submission.pk,
                                      "evaluator": self.instructor.pk,
                                      "teacher_comments": "",
                                      "instructor_notes": "testnotes",
                                      "criteria_answers": ''})
        assert resp.json()['instructor_notes'] == 'testnotes'
        assert resp.status_code == 201

        #  Tests that we can change any grade info using put method
        resp = self.client.put(path=reverse('api:grade-detail', kwargs={'version': 'v1', 'pk': '2'}),
                               data={"submission": self.submission.pk,
                                     "evaluator": self.instructor.pk,
                                     "teacher_comments": "",
                                     "instructor_notes": "changed instructor notes"},
                               content_type='application/json')
        assert resp.json()["instructor_notes"] == 'changed instructor notes'
        assert resp.status_code == 200

        #  Tests that we can delete a grade
        resp = self.client.delete(path=reverse('api:grade-detail', kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204

    @tag('incomplete')  #  Can't properly pass in "members" into the post request  "b'{"members":["This field is required."
    def test_crud_methods_on_teams(self):
        #  Tests that we can't retrieve a list of team using get method
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse('api:team-list', kwargs={'version': 'v1'}))
        assert resp.status_code == 200
        print(resp.content)

        #  Tests that we can post a new team
        resp = self.client.post(path=reverse('api:team-list', kwargs={'version': 'v1'}),
                                data={"klass": self.klass.pk,
                                      "name": "testteam",
                                      "description": "",
                                      "members": self.student.team.members})
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
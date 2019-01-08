# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from django.utils import timezone
#
# from apps.homework.models import Definition, Criteria, Submission, Question
# from apps.klasses.models import Klass
# from apps.profiles.models import Instructor, StudentMembership
#
# User = get_user_model()
#
#
# class PermissionTests(TestCase):
#
#     def setUp(self):
#         self.main_user = User.objects.create_user(username='user', password='pass')
#         self.main_user.set_password('pass')
#         self.main_user.save()
#         self.instructor = Instructor.objects.create(university_name='Test')
#         self.main_user.instructor = self.instructor
#         self.main_user.save()
#         self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
#
#         self.student_user = User.objects.create_user(username='student_user', password='pass', email="test@test.com")
#         self.student = StudentMembership.objects.create(user=self.student_user, klass=self.klass, student_id='test_id')
#
#         self.other_user = User.objects.create_user(username='other_user', password='pass')
#
#         self.definition = Definition.objects.create(
#             klass=self.klass,
#             creator=self.instructor,
#             due_date=timezone.now(),
#             name='test',
#             description='test'
#         )
#
#         self.question = Question.objects.create(
#             definition=self.definition,
#             question='Test Question',
#             answer='Test Answer'
#         )
#
#         self.criteria = Criteria.objects.create(
#             definition=self.definition,
#             description='Test Criteria',
#             lower_range=0,
#             upper_range=10
#         )
#
#         self.submission = Submission.objects.create(
#             definition=self.definition,
#             klass=self.klass,
#             creator=self.student
#         )
#
#     def test_user_permissions_as_anonymous_user(self):
#
#         self.client.logout()
#
#         resp = self.client.get(path='/api/v1/users/')
#         assert resp.status_code == 401
#
#         resp = self.client.post(path='/api/v1/users/', data={'username': 'new_user'})
#         assert resp.status_code == 401
#
#         resp = self.client.put(path='/api/v1/users/{}/'.format(self.main_user.pk), data={'username': 'new_user'},
#                                content_type='application/json')
#         assert resp.status_code == 401
#
#         resp = self.client.delete(path='/api/v1/users/{}/'.format(self.main_user.pk))
#         assert resp.status_code == 401
#
#     def test_user_permissions_as_authenticated_user(self):
#         # self.client.login(username='user', password='pass')
#         self.client.login(username='student_user', password='pass')
#
#         resp = self.client.get(path='/api/v1/users/')
#         assert resp.status_code == 200
#
#         resp = self.client.post(path='/api/v1/users/', data={'username': 'new_user'})
#         assert resp.status_code == 405
#
#         resp = self.client.put(path='/api/v1/users/{}/'.format(self.main_user.pk), data={'username': 'new_user'})
#         assert resp.status_code == 405
#
#         resp = self.client.delete(path='/api/v1/users/{}/'.format(self.main_user.pk))
#         assert resp.status_code == 405
#
#     def test_student_permissions_as_anonymous_user(self):
#         self.client.logout()
#
#         resp = self.client.get(path='/api/v1/students/')
#         assert resp.status_code == 401
#
#         resp = self.client.post(path='/api/v1/students/', data={'username': 'new_user'})
#         assert resp.status_code == 401
#
#         resp = self.client.put(path='/api/v1/students/{}/'.format(self.student.pk), data={'student_id': 'student_23'},
#                                content_type='application/json')
#         assert resp.status_code == 401
#
#         resp = self.client.delete(path='/api/v1/students/{}/'.format(self.main_user.pk))
#         assert resp.status_code == 401
#
#     def test_student_permissions_as_authenticated_user(self):
#         self.client.login(username='student_user', password='pass')
#
#         resp = self.client.get(path='/api/v1/students/')
#         assert resp.status_code == 200
#
#         resp = self.client.post(path='/api/v1/create_student/',
#                                 data={'email': self.student_user.email, 'student_id': 'student_23', 'klass': self.klass.pk})
#         assert resp.status_code == 404
#
#         # TODO: RE-VISIT PUT ON STUDENT (Fields on serializer are making it difficult)
#
#         resp = self.client.get(path='/api/v1/students/{}/'.format(self.student.pk))
#         assert resp.status_code == 200
#
#         temp_data = resp.json()
#         temp_data['student_id'] = 'test_id_123'
#
#         print("!!!!!!!")
#         print(temp_data)
#         print("!!!!!!!")
#
#         resp = self.client.put(path='/api/v1/students/{}/'.format(self.student.pk), data=temp_data,
#                                content_type='application/json')
#         assert resp.status_code == 400
#
#         resp = self.client.delete(path='/api/v1/students/{}/'.format(self.student.pk))
#         assert resp.status_code == 204
#
#     def test_klass_permissions_as_anonymous_user(self):
#         self.client.logout()
#
#         resp = self.client.get(path='/api/v1/klasses/')
#         assert resp.status_code == 401
#
#         resp = self.client.post(path='/api/v1/klasses/', data={'title': 'Test', 'instructor': self.instructor.pk})
#         assert resp.status_code == 401
#
#         resp = self.client.put(path='/api/v1/klasses/{}/'.format(self.klass.pk),
#                                data={'title': 'A Different Name'},
#                                content_type='application/json')
#         assert resp.status_code == 401
#
#         resp = self.client.delete(path='/api/v1/klasses/{}/'.format(self.klass.pk))
#         assert resp.status_code == 401
#
#     def test_klass_permissions_as_klass_creator(self):
#         self.client.login(username='user', password='pass')
#
#         resp = self.client.get(path='/api/v1/klasses/')
#         assert resp.status_code == 200
#
#         resp = self.client.post(path='/api/v1/klasses/', data={'title': 'Test', 'instructor': self.instructor.pk, 'course_number': 2})
#         assert resp.status_code == 201
#
#         resp = self.client.put(path='/api/v1/klasses/{}/'.format(self.klass.pk),
#                                data={'title': 'A Different Name', 'instructor': self.instructor.pk, 'course_number': 1 },
#                                content_type='application/json')
#         assert resp.status_code == 200
#
#         resp = self.client.delete(path='/api/v1/klasses/{}/'.format(self.klass.pk))
#         assert resp.status_code == 204
#
#     def test_klass_permissions_as_klass_student(self):
#         self.client.login(username='student_user', password='pass')
#
#         resp = self.client.get(path='/api/v1/klasses/')
#         assert resp.status_code == 200
#
#         resp = self.client.post(path='/api/v1/klasses/', data={'title': 'Test', 'instructor': self.instructor.pk, 'course_number': 2})
#         # TODO: Block this
#         # assert resp.status_code == 401
#
#         resp = self.client.put(path='/api/v1/klasses/{}/'.format(self.klass.pk),
#                                data={'title': 'A Different Name', 'instructor': self.instructor.pk, 'course_number': 1 },
#                                content_type='application/json')
#         assert resp.status_code == 403
#
#         resp = self.client.delete(path='/api/v1/klasses/{}/'.format(self.klass.pk))
#         assert resp.status_code == 403
#
#     def test_definition_permissions_as_anonymous_user(self):
#         self.client.logout()
#
#         resp = self.client.get(path='/api/v1/definitions/')
#         assert resp.status_code == 401
#
#         resp = self.client.post(path='/api/v1/definitions/', data={'klass': self.klass.pk,
#                                                                    'creator': self.instructor.pk,
#                                                                    'due_date': timezone.now(),
#                                                                    'name': 'test',
#                                                                    'description': 'test'})
#         assert resp.status_code == 401
#
#         resp = self.client.put(path='/api/v1/definitions/{}/'.format(1),
#                                data={'name': 'A Different Name'},
#                                content_type='application/json')
#         assert resp.status_code == 401
#
#         resp = self.client.delete(path='/api/v1/definitions/{}/'.format(1))
#         assert resp.status_code == 401
#
#     def test_definition_permissions_as_klass_creator(self):
#         """Tests that we can retrieve a list of users"""
#         self.client.login(username='user', password='pass')
#
#         resp = self.client.get(path='/api/v1/definitions/')
#         assert resp.status_code == 200
#
#         resp = self.client.post(path='/api/v1/definitions/', data={'klass': self.klass.pk,
#                                                                    'creator': self.instructor.pk,
#                                                                    'due_date': timezone.now(),
#                                                                    'name': 'test',
#                                                                    'description': 'test'})
#         assert resp.status_code == 201
#
#         resp = self.client.put(path='/api/v1/definitions/{}/'.format(1),
#                                data={'name': 'A Different Name', 'klass': self.klass.pk, 'creator': self.instructor.pk},
#                                content_type='application/json')
#         assert resp.status_code == 200
#
#         resp = self.client.delete(path='/api/v1/definitions/{}/'.format(1))
#         assert resp.status_code == 204
#
#     def test_definition_permissions_as_klass_student(self):
#         """Tests that we can retrieve a list of users"""
#         self.client.login(username='student_user', password='pass')
#
#         resp = self.client.get(path='/api/v1/definitions/')
#         assert resp.status_code == 200
#
#         resp = self.client.post(path='/api/v1/definitions/', data={'klass': self.klass.pk,
#                                                                    'creator': self.instructor.pk,
#                                                                    'due_date': timezone.now(),
#                                                                    'name': 'test',
#                                                                    'description': 'test'})
#         assert resp.status_code == 201
#
#         resp = self.client.put(path='/api/v1/definitions/{}/'.format(1),
#                                data={'name': 'A Different Name', 'klass': self.klass.pk, 'creator': self.instructor.pk},
#                                content_type='application/json')
#         assert resp.status_code == 403
#
#         resp = self.client.delete(path='/api/v1/definitions/{}/'.format(1))
#         assert resp.status_code == 403
#
#     def test_criteria_permissions_as_anonymous_user(self):
#         """Tests that we can retrieve a list of users"""
#         self.client.logout()
#
#         resp = self.client.get(path='/api/v1/criterias/')
#         assert resp.status_code == 401
#
#         resp = self.client.post(path='/api/v1/criterias/', data={'description': 'test',
#                                                                  'lower_range': 0,
#                                                                  'upper_range': 10})
#         assert resp.status_code == 401
#
#         resp = self.client.put(path='/api/v1/criterias/{}/'.format(1),
#                                data={'description': 'test',
#                                      'lower_range': 0,
#                                      'upper_range': 10},
#                                content_type='application/json')
#         assert resp.status_code == 401
#
#         resp = self.client.delete(path='/api/v1/criterias/{}/'.format(1))
#         assert resp.status_code == 401
#
#     def test_criteria_permissions_as_authenticated_user(self):
#         self.client.login(username='user', password='pass')
#         resp = self.client.get(path='/api/v1/criterias/')
#         assert resp.status_code == 401
#
#         resp = self.client.delete(path='/api/v1/criterias/{}/'.format(1))
#         assert resp.status_code == 401

import os

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.api.views.profiles import make_ordinal
from apps.profiles.models import Instructor
from apps.klasses.models import Klass

User = get_user_model()


def test_make_ordinal():
    assert make_ordinal(5) == '5th'
    assert make_ordinal(293) == '293rd'
    assert make_ordinal(2) == '2nd'
    assert make_ordinal(111) == '111th'
    assert make_ordinal(400) == '400th'


class ProfilesIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.user.instructor = self.instructor
        self.user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")

    def test_normal_csv_upload(self):
        self.client.force_login(self.user)
        initial_student_count = self.klass.enrolled_students.count()
        normal_csv_filename = os.path.join(os.path.dirname(settings.BASE_DIR), 'apps/api/tests/files/sample_upload_csvs/normal.csv')

        with open(normal_csv_filename, 'r+') as f:
            resp = self.client.post(reverse('api:create_students_from_csv', kwargs={'version': 'v1'}), {'file': f, 'klass': self.klass.pk})
            assert resp.status_code == 200

        final_student_count = self.klass.enrolled_students.count()
        assert final_student_count - initial_student_count == 3

    def test_lowercase_header_column_csv_upload(self):
        self.client.force_login(self.user)
        initial_student_count = self.klass.enrolled_students.count()
        normal_csv_filename = os.path.join(os.path.dirname(settings.BASE_DIR), 'apps/api/tests/files/sample_upload_csvs/lowercase_last_name.csv')

        with open(normal_csv_filename, 'r+') as f:
            resp = self.client.post(reverse('api:create_students_from_csv', kwargs={'version': 'v1'}), {'file': f, 'klass': self.klass.pk})
            assert resp.status_code == 200

        final_student_count = self.klass.enrolled_students.count()
        assert final_student_count - initial_student_count == 3

    def test_invalid_email_csv_upload(self):
        self.client.force_login(self.user)
        initial_student_count = self.klass.enrolled_students.count()
        normal_csv_filename = os.path.join(os.path.dirname(settings.BASE_DIR), 'apps/api/tests/files/sample_upload_csvs/invalid_email_2nd_student.csv')

        with open(normal_csv_filename, 'r+') as f:
            resp = self.client.post(reverse('api:create_students_from_csv', kwargs={'version': 'v1'}), {'file': f, 'klass': self.klass.pk})
            assert resp.status_code == 400

        final_student_count = self.klass.enrolled_students.count()
        assert final_student_count - initial_student_count == 1 # fails when creating second student, so one should exist


#     def test_get_users_works(self):
#         """Tests that we can retrieve a list of users"""
#         self.client.login(username='user', password='pass')
#
#         resp = self.client.get('/api/v1/users/')
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data[-1]['username'] == 'user'
#         assert data[-1]['id'] == self.user.pk
#
#     def test_get_single_user_works(self):
#         """Tests that we can retrieve our user from the API by PK"""
#         self.client.login(username='user', password='pass')
#
#         resp = self.client.get('/api/v1/users/{}/'.format(self.user.pk))
#         assert resp.status_code == 200
#         data = resp.json()
#         assert data['username'] == 'user'
#         assert data['id'] == self.user.pk
#
#     # def test_post_user_works(self):
#     #     """Tests that we can post the data for a new user to this API endpoint and it will create one"""
#     #     self.client.login(username='user', password='pass')
#     #
#     #     resp = self.client.post('/api/v1/users/', data={
#     #         'username': 'test-user',
#     #         # 'email': 'test-email'
#     #         'first_name': 'test',
#     #         'last_name': 'test'
#     #     })
#     #     user = User.objects.get(username='test-user')
#     #     assert user
#     #
#     # def test_put_user_works(self):
#     #     """Tests that we can update a user by put'ing data to this endpoint (For the specified ID)"""
#     #     self.client.login(username='user', password='pass')
#     #
#     #     resp = self.client.put('/api/v1/users/{}/'.format(self.user.pk), data={
#     #         'username': 'test-user',
#     #         'first_name': 'test',
#     #         'last_name': 'test',
#     #         'id': self.user.pk
#     #     }, content_type='application/json')
#     #     self.user.refresh_from_db()
#     #     assert self.user.username == 'test-user'
#     #     user = User.objects.get(username='test-user')
#     #     assert user
#
#
#     # Viewset excludes DELETE method. Other API endpoints will use this:
#
#     # def test_delete_user_works(self):
#     #     self.client.login(username='user', password='pass')
#     #
#     #     # This view takes a form to update a Klass object. Fields for the object must be on the form
#     #     # resp = self.client.put('/api/v1/users/{}/'.format(self.user.pk), data={
#     #     resp = self.client.delete('/api/v1/users/{}/'.format(self.user.pk))
#     #     print(resp.status_code)
#     #     import pdb; pdb.set_trace()
#     #     assert 0
#     #     # self.user.refresh_from_db()
#     #     # assert self.user.username == 'test-user'
#     #     # user = User.objects.get(username='test-user')
#     #     # assert user

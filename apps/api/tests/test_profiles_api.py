from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.klasses.models import Klass
from apps.profiles.models import Instructor

User = get_user_model()


class ProfilesIntegrationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.user.instructor = self.instructor
        self.user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")

    def test_get_users_works(self):
        """Tests that we can retrieve a list of users"""
        self.client.login(username='user', password='pass')

        resp = self.client.get(path='/api/v1/users/')
        assert resp.status_code == 200
        data = resp.json()
        assert data[-1]['username'] == 'user'
        assert data[-1]['id'] == self.user.pk

    def test_get_single_user_works(self):
        """Tests that we can retrieve our user from the API by PK"""
        self.client.login(username='user', password='pass')

        resp = self.client.get(path='/api/v1/users/{}/'.format(self.user.pk))
        assert resp.status_code == 200
        data = resp.json()
        assert data['username'] == 'user'
        assert data['id'] == self.user.pk

    # def test_post_user_works(self):
    #     """Tests that we can post the data for a new user to this API endpoint and it will create one"""
    #     self.client.login(username='user', password='pass')
    #
    #     resp = self.client.post(path='/api/v1/users/', data={
    #         'username': 'test-user',
    #         # 'email': 'test-email'
    #         'first_name': 'test',
    #         'last_name': 'test'
    #     })
    #     user = User.objects.get(username='test-user')
    #     assert user
    #
    # def test_put_user_works(self):
    #     """Tests that we can update a user by put'ing data to this endpoint (For the specified ID)"""
    #     self.client.login(username='user', password='pass')
    #
    #     resp = self.client.put(path='/api/v1/users/{}/'.format(self.user.pk), data={
    #         'username': 'test-user',
    #         'first_name': 'test',
    #         'last_name': 'test',
    #         'id': self.user.pk
    #     }, content_type='application/json')
    #     self.user.refresh_from_db()
    #     assert self.user.username == 'test-user'
    #     user = User.objects.get(username='test-user')
    #     assert user


    # Viewset excludes DELETE method. Other API endpoints will use this:

    # def test_delete_user_works(self):
    #     self.client.login(username='user', password='pass')
    #
    #     # This view takes a form to update a Klass object. Fields for the object must be on the form
    #     # resp = self.client.put(path='/api/v1/users/{}/'.format(self.user.pk), data={
    #     resp = self.client.delete(path='/api/v1/users/{}/'.format(self.user.pk))
    #     print(resp.status_code)
    #     import pdb; pdb.set_trace()
    #     assert 0
    #     # self.user.refresh_from_db()
    #     # assert self.user.username == 'test-user'
    #     # user = User.objects.get(username='test-user')
    #     # assert user
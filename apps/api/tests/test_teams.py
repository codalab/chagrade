import json
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership
User = get_user_model()


class TeamsAPIEndpointsTests(TestCase):

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
        self.klass = Klass.objects.create(
            instructor=self.instructor,
            course_number="1"
        )
        self.student = StudentMembership.objects.create(
            user=self.student_user,
            klass=self.klass,
            student_id='test_id'
        )

    def test_anonymous_permissions(self):

        resp = self.client.get(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 401

        resp = self.client.post(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}),
            data={"klass": '',
                  "name": "",
                  "description": "",
                  "members": ''})
        assert resp.status_code == 401

        resp = self.client.put(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': 1}),
            data={"klass": '',
                  "name": "",
                  "description": "",
                  "members": ''},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': 1}))
        assert resp.status_code == 401

    def test_authenticated_permissions(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}),
            data=json.dumps({"klass": self.klass.pk,
                  "name": "testteam",
                  "members": []}),
            content_type='application/json')
        assert resp.json()['name'] == 'testteam'
        assert resp.status_code == 201
        new_team_pk = resp.json()['id']

        resp = self.client.put(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': new_team_pk}),
            data=json.dumps({
                "name": 'newtestteam',
                "members": []}),
            content_type='application/json')
        assert resp.json()['detail'] == 'You are not allowed to use this resource.'
        assert resp.status_code == 403

        resp = self.client.delete(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': new_team_pk}))
        assert resp.json()['detail'] == "You are not allowed to use this resource."
        assert resp.status_code == 403

    def test_instructor_permissions(self):
        self.client.login(
            username='user',
            password='pass'
        )
        resp = self.client.get(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}),
            data=json.dumps({"klass": self.klass.pk,
                  "name": "testteam",
                  'members': []}),
            content_type='application/json')
        assert resp.json()['name'] == 'testteam'
        assert resp.status_code == 201
        new_team_pk = resp.json()['id']

        resp = self.client.put(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': new_team_pk}),
            data=json.dumps({
                "name": "newtestteamname",
                "members": []}),
            content_type='application/json')

        assert resp.json()['detail'] == 'You are not allowed to use this resource.'
        assert resp.status_code == 403

        resp = self.client.delete(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': new_team_pk}))
        assert resp.status_code == 403


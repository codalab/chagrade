from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, tag

from apps.groups.models import Team
from apps.klasses.models import Klass
from apps.profiles.models import Instructor, StudentMembership
User = get_user_model()


class TeamsAPIEndpointsTests(TestCase):

    def setUp(self):
        self.main_user = User.objects.create_user(username='user', password='pass')
        self.instructor = Instructor.objects.create(university_name='Test')
        self.main_user.instructor = self.instructor
        self.student_user = User.objects.create_user(username='student_user', password='pass')
        self.main_user.save()
        self.klass = Klass.objects.create(instructor=self.instructor, course_number="1")
        self.team = Team.objects.create(
            klass=self.klass)
        self.student = StudentMembership.objects.create(
            user=self.student_user,
            klass=self.klass,
            student_id='test_id',
            team=self.team)

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
            kwargs={'version': 'v1', 'pk': self.team.pk}),
            data={"klass": '',
                  "name": "",
                  "description": "",
                  "members": ''},
            content_type='application/json')
        assert resp.status_code == 401

        resp = self.client.delete(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': self.team.pk}))
        assert resp.status_code == 401

    def test_crud_methods_on_teams(self):
        self.client.login(username='student_user', password='pass')
        resp = self.client.get(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}),
            data={"klass": self.klass.pk,
                  "name": "testteam",
                  "description": "",
                  "members": self.student.pk})
        assert resp.status_code == 201

        resp = self.client.put(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': self.team.pk}),
            data={"klass": '',
                  "name": "",
                  "description": "",
                  "members": ''},
            content_type='application/json')
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': self.team.pk}))
        assert resp.status_code == 204

    @tag('current')
    def test_crud_methods_on_teams(self):
        self.client.login(username='user', password='pass')
        resp = self.client.get(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}))
        assert resp.status_code == 200

        resp = self.client.post(path=reverse(
            'api:team-list',
            kwargs={'version': 'v1'}),
            data={"klass": self.klass.pk,
                  "name": "testteam",
                  "description": "",
                  "members": self.student.pk})
        print(resp.content)
        assert resp.status_code == 201

        resp = self.client.put(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': '2'}),
            data={"klass": '',
                  "name": "",
                  "description": "",
                  "members": ''},
            content_type='application/json')
        assert resp.status_code == 200

        resp = self.client.delete(path=reverse(
            'api:team-detail',
            kwargs={'version': 'v1', 'pk': '2'}))
        assert resp.status_code == 204